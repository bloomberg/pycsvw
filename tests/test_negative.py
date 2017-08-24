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

import os
import io

import pytest

from pycsvw import CSVW
from pycsvw.csvw_exceptions import BothLangAndDatatypeError


def test_single_csv():

    metadata_path = "tests/simple.csv-metadata.json"
    metadata_url = "http://example.org/simple.metadata"
    csv_url = "http://example.org/simple.csv"
    csv_path = "tests/simple.csv"

    # Both metadata url and path
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=metadata_path, metadata_url=metadata_url, csv_path=csv_path)
    assert "only one argument of metadata_url and metadata_path" in str(exc.value)

    # No metadata
    with pytest.raises(ValueError) as exc:
        CSVW(csv_path=csv_path)
    assert "No metadata" in str(exc.value)

    # Only url or path for csv
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=metadata_path, csv_path=csv_path, csv_url=csv_url)
    assert "Only one of csv_url, csv_path or csv_handle" in str(exc.value)

    # No csv
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=metadata_path)
    assert "csv_url or csv_path or csv_handle argument required" in str(exc.value)

    # Table not specifying url
    with pytest.raises(ValueError) as exc:
        CSVW(csv_path=csv_path, metadata_path='tests/simple.no_url.csv-metadata.json')
    assert "should specify 'url'" in str(exc.value)


def test_multiple_csv():

    # Multiple csv expected but not found
    multiple_metadata_path = "tests/multiple_tables.csv-metadata.json"
    csv1_path = "tests/multiple1.csv"
    csv2_path = "tests/multiple2.csv"
    csv1_url = "http://wrong.org/Name-ID.csv"
    csv2_url = "http://wrong.org/ID-Age.csv"

    csv1_handle = io.StringIO(u"some text")
    csv2_handle = io.StringIO(u"some other text")
    csv3_handle = io.StringIO(u"yet another text")

    with pytest.raises(ValueError) as exc:
        csvw = CSVW(metadata_path=multiple_metadata_path, csv_path=csv1_path)
    assert "neither csv_url, csv_path nor csv_handle is a list or set or tuple." in str(exc.value)

    # Too little csv_handle
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=multiple_metadata_path, csv_handle=csv1_handle)
    assert "metadata (2)" in str(exc.value)
    assert "csv_handle's (1)" in str(exc.value)

    # Too many csv_handle
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=multiple_metadata_path,
             csv_handle=(csv1_handle, csv2_handle, csv3_handle))
    assert "metadata (2)" in str(exc.value)
    assert "csv_handle's (3)" in str(exc.value)

    # Too little csv_url
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=multiple_metadata_path, csv_url=csv1_url)
    assert "neither csv_url, csv_path nor csv_handle is a list or set or tuple." in str(exc.value)

    # Too little csv_path
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=multiple_metadata_path, csv_path=csv1_path)
    assert "neither csv_url, csv_path nor csv_handle is a list or set or tuple." in str(exc.value)

    # Both url and path
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=multiple_metadata_path,
             csv_path=(csv1_path, csv1_path),
             csv_url=(csv1_url, csv2_url))
    assert "Only one of csv_url, csv_path or csv_handle" in str(exc.value)

    urls_in_metadata = sorted({u"multiple_tables.ID-Age.csv", u"multiple_tables.Name-ID.csv"})

    # Urls do not match
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=multiple_metadata_path, csv_url=(csv1_url, csv2_url))
    msg = str(exc.value)
    csv_urls = sorted({csv1_url, csv2_url})
    assert "but not in csv_url are={}.".format(urls_in_metadata) in msg
    assert "but not in metadata are={}.".format(csv_urls) in msg

    # Paths do not match
    with pytest.raises(ValueError) as exc:
        CSVW(metadata_path=multiple_metadata_path, csv_path=(csv1_path, csv2_path))
    msg = str(exc.value)
    csv_paths = sorted({os.path.basename(csv1_path), os.path.basename(csv2_path)})
    assert "but not in csv_path file names are={}.".format(urls_in_metadata) in msg
    assert "but not in metadata are={}.".format(csv_paths) in msg


@pytest.mark.parametrize("metadata_file", [
    "tests/simple.BothLangAndDatatypeError1.csv-metadata.json",
    "tests/simple.BothLangAndDatatypeError2.csv-metadata.json",
    "tests/simple.BothLangAndDatatypeError3.csv-metadata.json"
])
def test_metadata_has_both_lang_and_datatype(metadata_file):
    with pytest.raises(BothLangAndDatatypeError):
        CSVW(csv_path="tests/simple.csv", metadata_path=metadata_file)


def test_json_generation():
    """Will remove this test when we add json generation support."""
    csvw = CSVW(csv_path="tests/simple.csv",
                metadata_path="tests/simple.csv-metadata.json")
    with pytest.raises(NotImplementedError) as exc:
        csvw.to_json()
    assert "JSON generation" in str(exc.value)








