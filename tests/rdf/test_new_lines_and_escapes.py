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
from rdflib.namespace import Namespace

from pycsvw import CSVW


def test_literals_with_new_lines():
    csv_path = "tests/parsing.quoted_newlines.csv"
    metadata_path = "tests/parsing.quoted_newlines.csv-metadata.json"
    csvw = CSVW(csv_path=csv_path,
                metadata_path=metadata_path)

    rdf_contents = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_contents, format="turtle")

    ns = Namespace("http://example.org/expense/")
    desc = URIRef("http://example.org/desc")

    taxi_triples = list(g.triples((ns['taxi'], desc, None)))
    assert len(taxi_triples) == 1
    taxi_desc = taxi_triples[0][2]
    assert isinstance(taxi_desc, Literal)
    assert len(taxi_desc.value.splitlines()) == 2

    flight = URIRef("http://example.org/expense/multi-hop%20flight")
    flight_triples = list(g.triples((flight, desc, None)))
    assert len(flight_triples) == 1
    flight_desc = flight_triples[0][2]
    assert isinstance(flight_desc, Literal)
    assert len(flight_desc.value.splitlines()) == 4

    dinner_triples = list(g.triples((ns['dinner'], desc, None)))
    assert len(dinner_triples) == 1
    dinner_desc = dinner_triples[0][2]
    assert isinstance(dinner_desc, Literal)
    assert u'\u2019' in dinner_desc, "Expected to read unicode characters"
    assert u"('')" in dinner_desc, "Expected to read apostrophes"


def test_literals_with_escaped_quotes():
    csv_path = "tests/parsing.escaped_quotes.csv"
    metadata_path = "tests/parsing.escaped_quotes.csv-metadata.json"
    csvw = CSVW(csv_path=csv_path,
                metadata_path=metadata_path)

    rdf_contents = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_contents, format="turtle")

    ns = Namespace("http://example.org/expense/")
    desc = URIRef("http://example.org/desc")

    taxi_triples = list(g.triples((ns['taxi'], desc, None)))
    assert len(taxi_triples) == 1
    taxi_desc = taxi_triples[0][2]
    assert isinstance(taxi_desc, Literal)
    assert taxi_desc.value == "go from x to y"

    quoted_expense_triples = list(g.triples((URIRef("http://example.org/expense/quoted%20expense"), desc, None)))
    assert len(quoted_expense_triples) == 1
    quoted_expense_desc = quoted_expense_triples[0][2]
    assert isinstance(quoted_expense_desc, Literal)
    assert quoted_expense_desc.value == "for some reason it came with quotes in it"

    flight_triples = list(g.triples((ns['flight'], desc, None)))
    assert len(flight_triples) == 1
    flight_desc = flight_triples[0][2]
    assert isinstance(flight_desc, Literal)
    assert flight_desc.value == "had to fly \"escaped quotes business\" for this trip"

    car_triples = list(g.triples((ns['car'], desc, None)))
    assert len(car_triples) == 1
    car_desc = car_triples[0][2]
    assert isinstance(car_desc, Literal)
    assert car_desc.value == " some \ in it to be escaped"




