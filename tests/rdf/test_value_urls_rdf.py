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

from rdflib import ConjunctiveGraph, BNode, Literal, RDF, RDFS, OWL
from rdflib.namespace import XSD, Namespace
import pytest

from pycsvw import CSVW


NS = Namespace('http://example.org/')


def test_multiple_value_urls_in_virtual():
    csvw = CSVW(csv_path="tests/value_urls.csv",
                metadata_path="tests/value_urls.csv-metadata.json")
    rdf_contents = csvw.to_rdf(fmt="nt")
    g = ConjunctiveGraph()
    g.parse(data=rdf_contents, format="nt")



    # Test subjects
    all_subjects = list(g.subjects())
    s_amount = NS['amount']
    s_desc = NS['description']
    s_id = NS['id']
    assert s_amount in all_subjects
    assert s_desc in all_subjects
    assert s_id in all_subjects

    # Test descriptions
    p_def = NS['definition']
    assert len(list(g.triples((s_amount, p_def, Literal("the amount paid"))))) == 1
    assert len(list(g.triples((s_desc, p_def, Literal("description of the expense"))))) == 1
    assert len(list(g.triples((s_id, p_def, Literal("transaction id"))))) == 1

    # Test each is a element type
    o_element = NS['element']
    assert len(list(g.triples((s_amount, RDF.type, o_element)))) == 1
    assert len(list(g.triples((s_desc, RDF.type, o_element)))) == 1
    assert len(list(g.triples((s_id, RDF.type, o_element)))) == 1

    # Test that range is specified
    r_amount = NS['element/amount-RANGE']
    r_desc = NS['element/description-RANGE']
    r_id = NS['element/id-RANGE']

    assert len(list(g.triples((s_amount, RDFS.range, r_amount)))) == 1
    assert len(list(g.triples((s_desc, RDFS.range, r_desc)))) == 1
    assert len(list(g.triples((s_id, RDFS.range, r_id)))) == 1

    # Range is another subject
    assert r_amount in all_subjects
    assert r_desc in all_subjects
    assert r_id in all_subjects

    # Range is a OWL datatype of specified type
    assert len(list(g.triples((r_amount, OWL.onDatatype, XSD.decimal)))) == 1
    assert len(list(g.triples((r_desc, OWL.onDatatype, XSD.string)))) == 1
    assert len(list(g.triples((r_id, OWL.onDatatype, XSD.integer)))) == 1

    # Check the restrictions for amount
    rest_amount_node = list(g.triples((r_amount, OWL.withRestrictions, None)))
    rest_amount_node = rest_amount_node[0][2]
    assert isinstance(rest_amount_node, BNode)
    assert len(list(g.triples((rest_amount_node, RDF.first, XSD.decimal)))) == 1
    rest_amount_node = next(g.objects(subject=rest_amount_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_amount_node, RDF.first, XSD.MaxLength)))) == 1
    rest_amount_node = next(g.objects(subject=rest_amount_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_amount_node, RDF.first,
                               Literal(10, datatype=XSD.nonNegativeInteger))))) == 1
    rest_amount_node = next(g.objects(subject=rest_amount_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_amount_node, RDF.first, XSD.MinLength)))) == 1
    rest_amount_node = next(g.objects(subject=rest_amount_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_amount_node, RDF.first,
                               Literal(1, datatype=XSD.nonNegativeInteger))))) == 1
    rest_amount_node = next(g.objects(subject=rest_amount_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_amount_node, RDF.first, None)))) == 0
    assert len(list(g.triples((rest_amount_node, RDF.rest, None)))) == 0

    # Check the restrictions for description
    rest_desc_node = list(g.triples((r_desc, OWL.withRestrictions, None)))
    rest_desc_node = rest_desc_node[0][2]
    assert isinstance(rest_desc_node, BNode)
    assert len(list(g.triples((rest_desc_node, RDF.first, XSD.string)))) == 1
    rest_desc_node = next(g.objects(subject=rest_desc_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_desc_node, RDF.first, XSD.MaxLength)))) == 1
    rest_desc_node = next(g.objects(subject=rest_desc_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_desc_node, RDF.first,
                               Literal(100, datatype=XSD.nonNegativeInteger))))) == 1
    rest_desc_node = next(g.objects(subject=rest_desc_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_desc_node, RDF.first, None)))) == 0
    assert len(list(g.triples((rest_desc_node, RDF.rest, None)))) == 0

    # Check the restrictions for id
    rest_id_node = list(g.triples((r_id, OWL.withRestrictions, None)))
    rest_id_node = rest_id_node[0][2]
    assert isinstance(rest_id_node, BNode)
    assert len(list(g.triples((rest_id_node, RDF.first, XSD.integer)))) == 1
    rest_id_node = next(g.objects(subject=rest_id_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_id_node, RDF.first, XSD.MinLength)))) == 1
    rest_id_node = next(g.objects(subject=rest_id_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_id_node, RDF.first,
                               Literal(0, datatype=XSD.nonNegativeInteger))))) == 1
    rest_id_node = next(g.objects(subject=rest_id_node, predicate=RDF.rest))
    assert len(list(g.triples((rest_id_node, RDF.first, None)))) == 0
    assert len(list(g.triples((rest_id_node, RDF.rest, None)))) == 0

    # Check constant value for each
    const_prop = NS['another-list-value-with-constants']
    for s in [r_amount, r_id, r_desc]:
        constant_node = list(g.triples((r_amount, const_prop, None)))
        constant_node = constant_node[0][2]
        assert isinstance(constant_node, BNode)
        assert len(list(g.triples((constant_node, RDF.first, XSD.Length)))) == 1
        constant_node = next(g.objects(subject=constant_node, predicate=RDF.rest))
        assert len(list(g.triples((constant_node, RDF.first,
                                   Literal(1, datatype=XSD.nonNegativeInteger))))) == 1
        constant_node = next(g.objects(subject=constant_node, predicate=RDF.rest))
        assert len(list(g.triples((constant_node, RDF.first, None)))) == 0
        assert len(list(g.triples((constant_node, RDF.rest, None)))) == 0

    # Verify that empty valueUrl does not end up in graph or rdf contents
    assert NS['empty-list-predicate1'] not in list(g.objects())
    assert "empty-list-predicate1" not in rdf_contents

    # Verify that empty valueUrl does not end up in graph
    assert NS['empty-list-predicate2'] not in list(g.objects())
    assert "empty-list-predicate2" not in rdf_contents

    # Test total number of lists through rdf:nils in order to verify each list
    # ends up with a nil
    test_num_lists = 3 * 3  # 3 rows and 3 virtual list valued columns
    nil_text = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#nil> ."
    assert rdf_contents.count(nil_text) == test_num_lists


def test_negative():
    from pycsvw.csvw_exceptions import BothValueAndLiteralError, \
        BothValueAndDatatypeError, NoValueOrLiteralError, InvalidItemError

    csvw = CSVW(csv_path="tests/value_urls.csv",
                metadata_path="tests/value_urls.BothValueAndLiteralError.csv-metadata.json")
    with pytest.raises(BothValueAndLiteralError):
        print(csvw.to_rdf())

    csvw = CSVW(csv_path="tests/value_urls.csv",
                metadata_path="tests/value_urls.BothValueAndDatatypeError.csv-metadata.json")
    with pytest.raises(BothValueAndDatatypeError):
        print(csvw.to_rdf())

    csvw = CSVW(csv_path="tests/value_urls.csv",
                metadata_path="tests/value_urls.NoValueOrLiteralError.csv-metadata.json")
    with pytest.raises(NoValueOrLiteralError):
        print(csvw.to_rdf())

    csvw = CSVW(csv_path="tests/value_urls.csv",
                metadata_path="tests/value_urls.InvalidItemError.csv-metadata.json")
    with pytest.raises(InvalidItemError):
        print(csvw.to_rdf())







