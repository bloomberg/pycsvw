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

"""
This test covers the cases where no value is specified for a cell
"""

from rdflib import ConjunctiveGraph, Literal

from pycsvw import CSVW


def test_empty():

    csvw = CSVW(csv_path="tests/empty.csv",
                metadata_path="tests/empty.csv-metadata.json")
    rdf_output = csvw.to_rdf()

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    assert len(g) == 0


def test_empty_boolean():
    csvw = CSVW(csv_path="tests/empty.csv",
                metadata_path="tests/empty.bool.csv-metadata.json")
    rdf_output = csvw.to_rdf()

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    assert len(g) == 2
    assert len(list(g.triples((None, None, Literal(False))))) == 2

    csvw = CSVW(csv_path="tests/empty.csv",
                metadata_path="tests/empty.invalid_base.csv-metadata.json")
    rdf_output = csvw.to_rdf()

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    assert len(g) == 0


