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

import io
from builtins import str as text

from rdflib import ConjunctiveGraph
from mock import patch, Mock

from pycsvw import CSVW


def verify_rdf(rdf_output):
    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")
    assert len(g) == 6
    assert len(set(g.subjects())) == 2
    assert len(set(g.predicates())) == 3
    assert len(set(g.objects())) == 6


def test_single_table_using_handles():
    csv_path = "tests/simple.csv"
    metadata_path = "tests/simple.csv-metadata.json"

    with io.open(csv_path) as csv1_f, io.open(metadata_path, 'r') as metadata_f:
        csv_handle = io.StringIO(csv1_f.read())
        metadata = io.StringIO(metadata_f.read())

    csvw = CSVW(csv_handle=csv_handle, metadata_handle=metadata)
    rdf = csvw.to_rdf()

    verify_rdf(rdf)


def test_single_table_using_path():
    csv_path = "tests/simple.csv"
    metadata_path = "tests/simple.csv-metadata.json"

    csvw = CSVW(csv_path=csv_path, metadata_path=metadata_path)
    rdf = csvw.to_rdf()

    verify_rdf(rdf)


@patch("pycsvw.csvw.urlopen")
def test_single_table_using_url(mock_urlopen):
    csv_path = "tests/simple.csv"
    metadata_path = "tests/simple.csv-metadata.json"
    csv_url = "http://example.org/simple.csv"

    with io.open(csv_path) as csv1_f:
        csv1 = text(csv1_f.read())

    reader = Mock()
    reader.read.side_effect = [csv1]
    mock_urlopen.return_value = reader

    csvw = CSVW(csv_url=csv_url, metadata_path=metadata_path)
    rdf = csvw.to_rdf()

    verify_rdf(rdf)





