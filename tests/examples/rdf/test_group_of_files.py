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
https://www.w3.org/TR/2015/REC-csv2rdf-20151217/#example-public-sector-roles-and-salaries
"""
import io
import warnings

from mock import patch, Mock
import rdflib
from rdflib import URIRef, Literal
from rdflib.namespace import DCTERMS, Namespace, FOAF, XSD

from pycsvw import CSVW
from pycsvw.csvw_exceptions import RiotWarning

URL_TO_FILE = {
    "http://example.org/gov.uk/data/organizations.csv": "tests/examples/organizations.csv",
    "http://example.org/gov.uk/data/professions.csv": "tests/examples/professions.csv",
    "http://example.org/senior-roles.csv": "tests/examples/senior-roles.csv",
    "http://example.org/junior-roles.csv": "tests/examples/junior-roles.csv",
    "http://example.org/csv-metadata.json": "tests/examples/csv-metadata.json",
    "gov.uk/schema/organizations.json": "tests/examples/organizations.json",
    "gov.uk/schema/professions.json": "tests/examples/professions.json",
    "gov.uk/schema/senior-roles.json": "tests/examples/senior-roles.json",
    "gov.uk/schema/junior-roles.json": "tests/examples/junior-roles.json"
}


def get_url_from_file(url):
    with io.open(URL_TO_FILE[url], 'r', encoding="utf-8") as f:
        return f.read()


def dispatch_files_as_url(url):
    reader = Mock()
    contents = get_url_from_file(url)
    reader.read.return_value = contents
    return reader


@patch("pycsvw.csvw.urlopen")
def test_group_of_tables(mock_urlopen):
    mock_urlopen.side_effect = dispatch_files_as_url
    csv_urls = [
        "http://example.org/gov.uk/data/organizations.csv",
        "http://example.org/gov.uk/data/professions.csv",
        "http://example.org/senior-roles.csv",
        "http://example.org/junior-roles.csv"
    ]
    csvw = CSVW(csv_url=csv_urls,
                metadata_url="http://example.org/csv-metadata.json")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RiotWarning)
        rdf_output = csvw.to_rdf()
    g = rdflib.Graph().parse(data=rdf_output, format="turtle")

    org = Namespace("http://www.w3.org/ns/org#")
    post_in = URIRef("http://example.org/organization/hefce.ac.uk")
    grade = URIRef("http://example.org/gov.uk/def/grade")
    job = URIRef("http://example.org/gov.uk/def/job")
    prof = URIRef("http://example.org/gov.uk/def/profession")
    post = Namespace("http://example.org/organization/hefce.ac.uk/post/")
    person = Namespace("http://example.org/organization/hefce.ac.uk/person/")
    min_pay = URIRef("http://example.org/gov.uk/def/min_pay")
    max_pay = URIRef("http://example.org/gov.uk/def/max_pay")
    num_posts = URIRef("http://example.org/gov.uk/def/number_of_posts")

    post_90115 = post["90115"]
    post_90334 = post["90334"]
    p1 = person["1"]
    p2 = person["2"]

    post_90115_triples = list(g.triples((post_90115, None, None)))
    assert len(post_90115_triples) == 7
    assert (post_90115, DCTERMS.identifier, Literal("90115")) in post_90115_triples
    assert (post_90115, org.heldBy, p1) in post_90115_triples
    assert (post_90115, grade, Literal("SCS1A")) in post_90115_triples
    assert (post_90115, job, Literal("Deputy Chief Executive")) in post_90115_triples
    assert (post_90115, org.reportsTo, post_90334) in post_90115_triples
    assert (post_90115, prof, Literal("Finance")) in post_90115_triples
    assert (post_90115, org.postIn, post_in) in post_90115_triples

    p1_triples = list(g.triples((p1, None, None)))
    assert len(p1_triples) == 1
    assert (p1, FOAF.name, Literal("Steve Egan")) in p1_triples

    post_90334_triples = list(g.triples((post_90334, None, None)))
    assert len(post_90334_triples) == 6
    assert (post_90334, DCTERMS.identifier, Literal("90334")) in post_90334_triples
    assert (post_90334, org.heldBy, p2) in post_90334_triples
    assert (post_90334, grade, Literal("SCS4")) in post_90334_triples
    assert (post_90334, job, Literal("Chief Executive")) in post_90334_triples
    assert (post_90334, prof, Literal("Policy")) in post_90334_triples
    assert (post_90334, org.postIn, post_in) in post_90334_triples

    p2_triples = list(g.triples((p2, None, None)))
    assert len(p2_triples) == 1
    assert (p2, FOAF.name, Literal("Sir Alan Langlands")) in p2_triples

    bnode1 = list(g.triples((None, grade, Literal("4"))))[0][0]
    b1_triples = list(g.triples((bnode1, None, None)))
    assert len(b1_triples) == 8
    assert (bnode1, org.reportsTo, post_90115) in b1_triples
    assert (bnode1, min_pay, Literal(17426, datatype=XSD.integer)) in b1_triples
    assert (bnode1, max_pay, Literal(20002, datatype=XSD.integer)) in b1_triples
    assert (bnode1, job, Literal("Administrator")) in b1_triples
    assert (bnode1, num_posts, Literal(8.67, datatype=XSD.double)) in b1_triples
    assert (bnode1, prof, Literal("Operational Delivery")) in b1_triples
    assert (bnode1, org.postIn, post_in) in b1_triples

    bnode2 = list(g.triples((None, grade, Literal("5"))))[0][0]
    b2_triples = list(g.triples((bnode2, None, None)))
    assert len(b2_triples) == 8
    assert (bnode2, org.reportsTo, post_90115) in b2_triples
    assert (bnode2, min_pay, Literal(19546, datatype=XSD.integer)) in b2_triples
    assert (bnode2, max_pay, Literal(22478, datatype=XSD.integer)) in b2_triples
    assert (bnode2, job, Literal("Administrator")) in b2_triples
    assert (bnode2, num_posts, Literal(0.5, datatype=XSD.double)) in b2_triples
    assert (bnode2, prof, Literal("Operational Delivery")) in b2_triples
    assert (bnode2, org.postIn, post_in) in b2_triples

    assert len(list(g.triples((None, None, None)))) == 7+1+6+1+8+8

















