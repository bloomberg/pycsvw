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

from rdflib import ConjunctiveGraph
from rdflib.namespace import Namespace
from six.moves.urllib.parse import quote

from pycsvw import CSVW


def test_encoding_rdf():
    # With encoding specified
    encoding = "ISO-8859-1"
    csvw = CSVW(csv_path="./tests/iso_encoding.csv",
                metadata_path="./tests/iso_encoding.csv-metadata.json",
                csv_encoding=encoding)
    rdf_output = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    units = Namespace('http://example.org/units/')
    cars = Namespace('http://example.org/cars/')
    meta = Namespace("http://example.org/properties/")

    expected_unit = units[quote(u"\xb5100".encode('utf-8'))]
    assert (cars['1'], meta['UnitOfMeasurement'], expected_unit) in g
    assert expected_unit in list(g.objects())








