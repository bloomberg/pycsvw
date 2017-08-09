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

from mock import patch, Mock
from rdflib import ConjunctiveGraph, Literal, Namespace

from pycsvw import CSVW


def verify_rdf(rdf_output):
    ids_ns = Namespace("http://foo.example.org/CSV/People-IDs/")
    ages_ns = Namespace("http://foo.example.org/CSV/People-Ages/")
    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    all_subjects = {x for x in g.subjects()}
    assert len(all_subjects) == 2

    bob_subj = ids_ns['1']
    joe_subj = ids_ns['2']
    assert bob_subj in all_subjects
    assert joe_subj in all_subjects

    # Bob's details
    assert len([g.triples((bob_subj, ids_ns.id, Literal(1)))]) == 1
    assert len([g.triples((bob_subj, ids_ns.name, Literal("Bob")))]) == 1
    assert len([g.triples((bob_subj, ages_ns.age, Literal(34)))]) == 1

    # Joe's details
    assert len([g.triples((joe_subj, ids_ns.id, Literal(2)))]) == 1
    assert len([g.triples((joe_subj, ids_ns.name, Literal("Joe")))]) == 1
    assert len([g.triples((joe_subj, ages_ns.age, Literal(54)))]) == 1


def test_multiple_tables_through_handles():
    metadata_path = "tests/multiple_tables.csv-metadata.json"
    csv1_path = "tests/multiple_tables.Name-ID.csv"
    csv2_path = "tests/multiple_tables.ID-Age.csv"

    with io.open(metadata_path, 'r') as metadata_f, io.open(csv1_path) as csv1_f, io.open(csv2_path) as csv2_f:
        metadata = io.StringIO(metadata_f.read())
        csv1 = io.StringIO(csv1_f.read())
        csv2 = io.StringIO(csv2_f.read())

    csvw = CSVW(csv_handle=[csv1, csv2], metadata_handle=metadata)
    rdf = csvw.to_rdf()

    verify_rdf(rdf)


def test_multiple_tables_through_paths():
    metadata_path = "tests/multiple_tables.csv-metadata.json"
    csv1_path = "tests/multiple_tables.Name-ID.csv"
    csv2_path = "tests/multiple_tables.ID-Age.csv"

    with open(metadata_path, 'r') as metadata_f:
        metadata = io.StringIO(text(metadata_f.read()))

    csvw = CSVW(csv_path=(csv1_path, csv2_path), metadata_handle=metadata)
    rdf = csvw.to_rdf()

    verify_rdf(rdf)


@patch("pycsvw.csvw.urlopen")
def test_multiple_tables_through_urls(mock_urlopen):
    metadata_path = "tests/multiple_tables.csv-metadata.json"
    csv1_url = "multiple_tables.Name-ID.csv"
    csv2_url = "multiple_tables.ID-Age.csv"
    csv1_path = "tests/multiple_tables.Name-ID.csv"
    csv2_path = "tests/multiple_tables.ID-Age.csv"

    with io.open(metadata_path, 'r') as metadata_f, io.open(csv1_path) as csv1_f, io.open(csv2_path) as csv2_f:
        metadata = io.StringIO(text(metadata_f.read()))
        csv1 = text(csv1_f.read())
        csv2 = text(csv2_f.read())

    reader = Mock()
    reader.read.side_effect = [csv1, csv2]
    mock_urlopen.return_value = reader

    csvw = CSVW(csv_url=(csv1_url, csv2_url), metadata_handle=metadata)
    rdf = csvw.to_rdf()

    verify_rdf(rdf)



