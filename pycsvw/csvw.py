# Copyright 2017 Bloomberg Finance L.P.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Define CSVW class """
import io
import logging
import json
import os
from tempfile import gettempdir, NamedTemporaryFile
from subprocess import Popen, PIPE
import shlex
import warnings
from distutils.spawn import find_executable
import stat

from six.moves.urllib.request import urlopen  # pylint: disable=import-error
from six import string_types
from rdflib import Graph
from past.builtins import basestring

from . import nt_serializer
from .csvw_exceptions import NoDefaultOrValueUrlError, \
    BothDefaultAndValueUrlError, BothLangAndDatatypeError, RiotWarning, RiotError

READ_PERMISSIONS = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH


class CSVW(object):
    """ CSVW class to generate rdf/json given csv and its metadata. """

    @staticmethod
    def _read_metadata(handle):
        """ Read metadata json file.
        :param handle: File-like object of the metadata json file.
        :return: A dictionary representing the metadata.
        """
        contents = handle.read()
        md_json = json.loads(contents)
        out = md_json if "tables" in md_json else {"tables": [md_json]}
        # Add some default values here to avoid
        # calling dict.get() excessively during RDF/JSON generation
        # as well as some error-check

        for table in out["tables"]:
            # Each table should specify a url
            if "url" not in table:
                raise ValueError("Each table in metadata should specify 'url'.")
            table_schema = table["tableSchema"]
            if isinstance(table_schema, string_types):
                # This is a URL, read it from the source and replace
                schema_url = urlopen(table_schema)
                schema_contents = schema_url.read()
                table_schema = json.loads(schema_contents)
                table["tableSchema"] = table_schema
            table["suppressOutput"] = table.get("suppressOutput", False)
            table_schema["aboutUrl"] = table_schema.get("aboutUrl", None)
            for col in table_schema["columns"]:
                col["null"] = col.get("null", None)
                if col["null"]:
                    if isinstance(col["null"], string_types):
                        col["null"] = [col["null"]]
                    else:
                        col["null"] = [x for x in col["null"]]

                col["datatype"] = col.get("datatype", None)
                if "lang" in col and col["datatype"] != "string":
                    raise BothLangAndDatatypeError(
                        "Column {} should have either "
                        "lang or datatype, not both unless datatype='string'.".format(col))

                col["virtual"] = col.get("virtual", False)
                col["valueUrl"] = col.get("valueUrl", None)
                col["default"] = col.get("default", None)
                # Error check
                if col["virtual"]:
                    if col["valueUrl"] is None and col["default"] is None:
                        raise NoDefaultOrValueUrlError(
                            "Virtual column {} should have either "
                            "default or valueUrl.".format(col))
                    if col["valueUrl"] and col["default"]:
                        raise BothDefaultAndValueUrlError(
                            "Virtual column {} should have either "
                            "default or valueUrl, not both.".format(col))

                col["aboutUrl"] = col.get("aboutUrl", None)
                col["suppressOutput"] = col.get("suppressOutput", False)

        return out

    @staticmethod
    def _get_metadata_handle(metadata_url, metadata_path, metadata_handle):
        """ Process input arguments regarding metadata and 
        return file-like object read_metadataholding it."""
        if metadata_path and metadata_url:
            raise ValueError("only one argument of metadata_url and metadata_path allowed")
        elif metadata_url:
            meta_resp = urlopen(metadata_url)
            metadata_handle = io.StringIO(meta_resp.read())
        elif metadata_path:
            metadata_handle = io.open(metadata_path, 'r', encoding="utf-8")

        if metadata_handle is None:
            raise ValueError('No metadata is specified')

        return metadata_handle

    def _read_tables(self, table_urls, csv_url, csv_path, csv_handle, csv_encoding):
        """Read the CSV file(s) into tables"""

        csv_args = (csv_url, csv_path, csv_handle)
        len_csv_args = len([x for x in csv_args if x])
        if len_csv_args > 1:
            raise ValueError("Only one of csv_url, csv_path or csv_handle should be specified")
        elif len_csv_args == 0:
            raise ValueError("csv_url or csv_path or csv_handle argument required")

        # Multiple tables, they should be specified as multiple csv files
        # through a list of csv_urls or csv_paths
        if len(table_urls) > 1 and all([not isinstance(arg, (list, tuple, set)) for arg in csv_args]):
            raise ValueError(
                "Metadata indicates multiple csv files, yet neither csv_url, csv_path "
                "nor csv_handle is a list or set or tuple.")

        specified_by_url, specified_by_path = False, False
        # Check compliance between metadata and csv files
        if csv_url:
            specified_by_url = True
            if not isinstance(csv_url, basestring):
                # If specified by multiple urls, urls in metadata should match
                table_urls_set = set(table_urls)
                csv_set = set(csv_url)
                if table_urls_set != csv_set:
                    msg = """
                    Table urls in metadata do not match the elements in csv_url:
                    Urls in metadata but not in csv_url are={}. 
                    Urls in csv_url but not in metadata are={}.
                    """.format(sorted(table_urls_set - csv_set), sorted(csv_set - table_urls_set))
                    raise ValueError(msg)
        elif csv_path:
            specified_by_path = True
            # If specified by multiple paths, the file names should match urls in metadata
            if not isinstance(csv_path, basestring):
                file_names = [os.path.basename(x) for x in csv_path]
                table_urls_set = set(table_urls)
                file_names_set = set(file_names)
                if table_urls_set != file_names_set:
                    msg = """Table urls in metadata do not match the file names in csv_path:
                    Urls in metadata but not in csv_path file names are={}. 
                    File names in csv_path but not in metadata are={}.
                    """.format(sorted(table_urls_set - file_names_set),
                               sorted(file_names_set - table_urls_set))
                    raise ValueError(msg)
        else:
            if len(table_urls) != len(csv_handle):
                raise ValueError("Number of tables in metadata ({}) do not match the number of "
                                 "csv_handle's ({})".format(len(table_urls), len(csv_handle)))

        handle_offset = 0
        for table_url in table_urls:
            if specified_by_path:
                if isinstance(csv_path, basestring):
                    this_csv_handle = io.open(csv_path, 'r', encoding=csv_encoding)
                else:
                    # Find this one
                    csv_ind = file_names.index(table_url)
                    this_csv_handle = io.open(csv_path[csv_ind], 'r', encoding=csv_encoding)
            elif specified_by_url:
                url_resp = urlopen(table_url)
                this_csv_handle = io.StringIO(url_resp.read())
            else:
                this_csv_handle = csv_handle[handle_offset]
                handle_offset += 1
            self._tables[table_url] = this_csv_handle

    def __init__(self, csv_url=None, csv_path=None, csv_handle=None,
                 metadata_url=None, metadata_path=None, metadata_handle=None,
                 csv_encoding="utf-8", temp_dir=None, riot_path=None):
        self.temp_dir = temp_dir if temp_dir else gettempdir()
        self.riot_path = riot_path if riot_path else "riot"
        self._nt_output_file = None
        self._prefixes_ttl_file = None
        self._namespaces = {}
        # tables is a dictionary from table url to a file-like obj for csv file
        self._tables = {}
        # Put csv_handle into a list if it is specified
        if not isinstance(csv_handle, (list, set, tuple)) and csv_handle is not None:
            csv_handle = [csv_handle]

        metadata_handle = self._get_metadata_handle(metadata_url, metadata_path, metadata_handle)

        # Extract namespaces from metadata
        # Note that this throws warnings since curly braces are not valid URIs,
        # disable those warnings temporarily
        logging.disable(logging.WARNING)
        graph = Graph().parse(data=metadata_handle.read(), format="json-ld")
        logging.disable(logging.NOTSET)
        # Convert it into a dictionary
        self._namespaces = {prefix: url.toPython() for prefix, url in graph.namespaces()}
        # Set it back to the beginning of file
        metadata_handle.seek(0)

        # Read metadata - csv_url does not need to be passed if it is a list, since
        # urls have to be specified in metadata in that case anyhow.
        try:
            self._metadata = self._read_metadata(metadata_handle)
        finally:
            metadata_handle.close()
        # Get the table url(s), this will be used to map tables to corresponding metadata
        table_urls = [x["url"] for x in self._metadata["tables"]]

        # Read the table(s)
        self._read_tables(table_urls, csv_url, csv_path, csv_handle, csv_encoding)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        # Close all csv handles
        for t in self._tables:
            self._tables[t].close()

        # Remove temporary files
        if self._nt_output_file:
            os.remove(self._nt_output_file)
        if self._prefixes_ttl_file:
            os.remove(self._prefixes_ttl_file)

    def to_rdf_files(self, file_format_tuples):
        """ Generate rdf serializations for specified formats into the specified file objects.
        :param file_format_tuples: A list of tuples of file-like object and format string. Example:
        [(ttl_file_obj, "turtle"), (nt_file_obj, "nt")]
        :return: None.
        """
        if self._nt_output_file is None or not os.path.exists(self._nt_output_file):
            nt_out = NamedTemporaryFile(dir=self.temp_dir, suffix=".nt", delete=False)
            nt_serializer.serialize(self._tables,
                                    self._metadata["tables"],
                                    self._namespaces,
                                    nt_out)
            self._nt_output_file = nt_out.name
            nt_out.close()
            os.chmod(self._nt_output_file, READ_PERMISSIONS)

        riot_checked = False
        for file_obj, fmt in file_format_tuples:
            if fmt.upper() in ["NT", "N-TRIPLE", "N-TRIPLES"]:
                # Write the contents of serialized NT directly
                with io.open(self._nt_output_file, 'r', encoding="utf-8", newline='') as nt_file:
                    file_obj.write(nt_file.read().encode("utf-8"))
            else:
                # Compute prefixes file
                if self._prefixes_ttl_file is None and self._namespaces != {}:
                    prefixes_ttl = NamedTemporaryFile(dir=self.temp_dir,
                                                      suffix=".ttl", delete=False)
                    self._prefixes_ttl_file = prefixes_ttl.name
                    for pre, url in self._namespaces.items():
                        prefixes_ttl.write(u"@prefix {}: <{}> .\n".format(pre, url).encode('utf-8'))
                    prefixes_ttl.close()
                    os.chmod(self._prefixes_ttl_file, READ_PERMISSIONS)
                prefixes = self._prefixes_ttl_file + " " if self._namespaces != {} else ""

                # Check that 'riot' is command in the system path
                if (not riot_checked) and find_executable(self.riot_path) is None:
                    raise ValueError("Could not locate '{}' in the system".format(self.riot_path))
                riot_checked = True

                # Translate RDF to RDFXML and XML to RDFXML
                fmt = "RDFXML" if fmt.upper() == "RDF" or fmt.upper() == "XML" else fmt

                cmd = self.riot_path + " --formatted='{}' {} {}".format(
                    fmt, prefixes, self._nt_output_file)
                err = PIPE
                riot_process = Popen(shlex.split(cmd), stdout=file_obj, stderr=err)
                file_obj, err = riot_process.communicate()
                if riot_process.returncode != 0:
                    raise RiotError(
                        "The riot command='{}' returned with following rc={} and error:\n"
                        "{}".format(cmd, riot_process.returncode, err))
                if err:
                    # Report riot warnings
                    warnings.warn(RiotWarning("cmd='{}' generated riot warnings:\n{}".format(
                        cmd, err)))

    def to_rdf(self, fmt="turtle"):
        """ Return rdf serialization for the specified format as unicode."""
        with NamedTemporaryFile(dir=self.temp_dir, delete=True) as out:
            self.to_rdf_files([(out, fmt)])
            out.seek(0)
            output = out.read().decode("utf-8")
        return output

    def to_json(self):
        """ Generate JSON serialization. """
        raise NotImplementedError("JSON generation is not supported yet.")
