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

""" Command line interface for pycsvw """
import json
import io

import click  # pylint: disable=import-error

from pycsvw import CSVW


@click.command()
@click.option("--csv-url", nargs=1, type=str, multiple=True, help="URL of the CSVW")
@click.option("--csv-path", nargs=1, type=str, multiple=True, help="System path to the CSVW")
@click.option("--metadata-url", help="URL of the CSVW metadata")
@click.option("--metadata-path", help="System path to the CSVW metadata")
@click.option("--json-dest", help="Destination of the JSON file to generate")
@click.option("--rdf-dest", nargs=2, type=str, multiple=True,
              help="Pair of format and destination path of RDF e.g. 'turtle out.ttl'")
@click.option("--temp-dir", help="Use as the temporary folder for (intermediate) nt serialization")
@click.option("--riot-path", help="The path to the riot command e.g. '/usr/bin/jena/bin/riot'")
def main(csv_url, csv_path, metadata_url, metadata_path, json_dest, rdf_dest, temp_dir, riot_path):
    """ Command line interface for pycsvw."""
    # Handle no csv_path, single one and multiple ones
    if csv_path == ():
        csv_path = None
    elif len(csv_path) == 1:
        csv_path = csv_path[0]

    with CSVW(csv_url=csv_url if csv_url else None,
              csv_path=csv_path,
              metadata_url=metadata_url,
              metadata_path=metadata_path,
              temp_dir=temp_dir,
              riot_path=riot_path) as csvw:

        for form, dest in rdf_dest:
            rdf_output = csvw.to_rdf(form)
            with io.open(dest, "wb") as rdf_file:
                rdf_file.write(rdf_output.encode('utf-8'))
        if json_dest:
            json_output = csvw.to_json()
            with open(json_dest, "w") as json_file:
                json.dump(json_output, json_file, indent=2)
