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

from rdflib import ConjunctiveGraph, URIRef, Literal
from rdflib.namespace import XSD, Namespace

from pycsvw import CSVW


subj_ns = Namespace("http://keys.example.org/")
sect_uri = URIRef("http://www.example.org/sector")
id_uri = URIRef("http://www.example.org/id")


def test_null_values_with_single_string():
    csvw = CSVW(csv_path="tests/null1.csv",
                metadata_path="tests/null1.single.csv-metadata.json")
    rdf_contents = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_contents, format="turtle")

    # There should be no subject NA
    all_subjects = {x for x in g.subjects()}
    assert subj_ns['null_key'] not in all_subjects
    assert subj_ns['1'] in all_subjects
    assert len(all_subjects) == 4

    # Null valued objects should not be created
    all_objects = {x for x in g.objects()}
    assert Literal('null_key', datatype=XSD.token) not in all_objects
    assert Literal('null_sector') not in all_objects
    assert Literal('null_id', datatype=XSD.token) not in all_objects
    assert Literal('PUBLIC') in all_objects
    assert Literal('12', datatype=XSD.token) in all_objects

    # Spot check some triples do not exist but other do from the same row
    null_key_lit = Literal('null_id', datatype=XSD.token)
    assert len(list(g.triples((subj_ns['2'], id_uri, null_key_lit)))) == 0

    priv_lit = Literal('PRIVATE')
    assert len(list(g.triples((subj_ns['2'], sect_uri, priv_lit)))) == 1

    null_sector_lit = Literal('null_sector')
    assert len(list(g.triples((subj_ns['3'], sect_uri, null_sector_lit)))) == 0

    twelve_lit = Literal('12', datatype=XSD.token)
    assert len(list(g.triples((subj_ns['3'], id_uri, twelve_lit)))) == 1


def test_null_values_with_multiple_strings():
    csvw = CSVW(csv_path="tests/null1.csv",
                metadata_path="tests/null1.multiple.csv-metadata.json")
    rdf_contents = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_contents, format="turtle")

    all_objects = {x for x in g.objects()}

    assert Literal('null_key', datatype=XSD.token) not in all_objects
    assert Literal('null_sector') not in all_objects
    assert Literal('null_id', datatype=XSD.token) not in all_objects
    for id in ['10', '11', '12', '13']:
        assert Literal(id, datatype=XSD.token) not in all_objects

    all_preds = {x for x in g.predicates()}
    assert id_uri not in all_preds

    assert Literal('1', datatype=XSD.token) not in all_objects


















