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

""" Tests that the example at the following link in W3C CSVW spec works as expected: 
https://www.w3.org/TR/2015/REC-csv2rdf-20151217/#example-tree-ops-ext
"""
from datetime import date
import xml

import rdflib
from past.builtins import long

from pycsvw import CSVW


def test_rdf_tree_ops_ext():
    # Generate rdf

    csvw = CSVW(csv_path="tests/examples/tree-ops-ext.csv", metadata_path="tests/examples/tree-ops-ext.csv-metadata.json")
    rdf_output = csvw.to_rdf()
    g = rdflib.Graph().parse(data=rdf_output, format="turtle")

    # Validate rdf
    total_triples = (9-1)*3 - 2 + 7 # 9 columns, 1 suppressed, two null comments and 7 separated comments
    assert len(g) == total_triples, "Expecting a total of {} triples".format(total_triples)

    table_url = "http://example.org/tree-ops-ext.csv"
    # Subject
    subjects = set([x for x in g.subjects()])
    assert len(subjects) == 3, "Expecting 3 subjects, one for each row"
    # Subjects should be named as specified by aboutURL and primary key
    expected_preds = ["on_street", "species", "trim_cycle", "dbh",
                      "inventory_date", "protected", "kml"]
    pred_comments = rdflib.URIRef("{}#comments".format(table_url))
    for ind in [1, 2, 6]:
        uri = rdflib.URIRef("http://example.org/tree-ops-ext#gid-{}".format(ind))
        assert uri in subjects, "{} not among subjects".format(uri)
        triples = [t for t in g.triples((uri, None, None))]
        preds = [x[1] for x in triples]
        for p in expected_preds:
            p_uri = rdflib.URIRef("{}#{}".format(table_url, p))
            assert p_uri in preds, "Predicate {} expected to be in triples of {}".format(
                p_uri, uri)

        if ind == 6:
            assert len(triples) == 15, "{} expected to have 15 triples".format(uri)
            assert pred_comments in preds, "Predicate {} should not be there for {}".format(
                pred_comments, uri)
        else:
            assert len(triples) == 7, "{} expected to have 7 triples".format(uri)
            assert pred_comments not in preds, "Predicate {} should be there for {}".format(
                pred_comments, uri)

    # Predicates
    predicates = set([x for x in g.predicates()])
    assert len(predicates) == 8, "Expecting 8 different predicates"

    # Objects
    on_street_objs = []
    for t in g.triples((None, rdflib.URIRef("{}#on_street".format(table_url)), None)):
        on_street_objs.append(t[2])
    assert len(on_street_objs) == 3, "There should be 3 on_street triples"
    for o in on_street_objs:
        assert o.datatype is None, "datatype should not be specified for on_street data"
        assert o.language is None, "language should not be specified for on_street data"

    species_objs = []
    for t in g.triples((None, rdflib.URIRef("{}#species".format(table_url)), None)):
        species_objs.append(t[2])
    assert len(species_objs) == 3, "There should be 3 species triples"
    for o in species_objs:
        assert o.datatype is None, "datatype should not be specified for species data"
        assert o.language is None, "language should not be specified for species data"

    trim_cycle_objs = []
    for t in g.triples((None, rdflib.URIRef("{}#trim_cycle".format(table_url)), None)):
        trim_cycle_objs.append(t[2])
    assert len(trim_cycle_objs) == 3, "There should be 3 trim_cycle triples"
    for o in trim_cycle_objs:
        assert o.datatype is None, "datatype should not be specified for trim_cycle data"
        assert str(o.language) == "en", "language should be specified as en for trim_cycle data"

    dbh_objs = []
    for t in g.triples((None, rdflib.URIRef("{}#dbh".format(table_url)), None)):
        dbh_objs.append(t[2])
    assert len(dbh_objs) == 3, "There should be 3 dbh triples"
    for o in dbh_objs:
        assert isinstance(o.value, long), "dbh should be an integer"
        assert o.datatype == rdflib.XSD.integer, "datatype should be specified as integer for dbh data"
        assert o.language is None, "language should not be specified for dbh data"

    inv_date_objs = []
    for t in g.triples((None, rdflib.URIRef("{}#inventory_date".format(table_url)), None)):
        inv_date_objs.append(t[2])
    assert len(inv_date_objs) == 3, "There should be 3 inventory_date triples"
    for o in inv_date_objs:
        assert isinstance(o.value, date), "inventory_date should be a date"
        assert o.value.year == 2010, "inventory_date year should be 2010"
        assert o.datatype == rdflib.XSD.date, "datatype should be specified as date for inventory_date data"
        assert o.language is None, "language should not be specified for dbh data"

    protected_objs = []
    for t in g.triples((None, rdflib.URIRef("{}#protected".format(table_url)), None)):
        protected_objs.append(t[2])
    assert len(protected_objs) == 3, "There should be 3 protected triples"
    for o in protected_objs:
        assert isinstance(o.value, bool), "protected should be a bool"
        assert o.datatype == rdflib.XSD.boolean, "datatype should be specified as bool for protected data"
        assert o.language is None, "language should not be specified for protected data"

    kml_objs = []
    for t in g.triples((None, rdflib.URIRef("{}#kml".format(table_url)), None)):
        kml_objs.append(t[2])
    assert len(kml_objs) == 3, "There should be 3 dbh triples"
    for o in kml_objs:
        assert isinstance(o.value, xml.dom.minidom.Document), "kml should be an XML document"
        assert o.datatype == rdflib.RDF.XMLLiteral, "datatype should be specified as xml for kml data"
        assert o.language is None, "language should not be specified for kml data"

    comments_objs = []
    for t in g.triples((None, pred_comments, None)):
        comments_objs.append(t[2])
    assert len(comments_objs) == 8, "There should be 8 comments"
    for o in comments_objs:
        assert o.datatype is None, "datatype should not be specified for comments data"
        assert o.language is None, "language should not be specified for comments data"