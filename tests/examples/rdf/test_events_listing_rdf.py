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
https://www.w3.org/TR/2015/REC-csv2rdf-20151217/#example-events-listing
"""
import warnings

import rdflib

from pycsvw import CSVW
from pycsvw.csvw_exceptions import RiotWarning


def test_rdf_events_listing():
    # Generate rdf
    csvw = CSVW(csv_path="tests/examples/events-listing.csv",
                metadata_path="tests/examples/events-listing.csv-metadata.json")
    # RIOT throws relative IRI warnings for this example.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RiotWarning)
        rdf_output = csvw.to_rdf()
    g = rdflib.Graph().parse(data=rdf_output, format="turtle")
    assert len(g) == 20, "Expected 20 triples"

    # Subjects
    subjects = set([x for x in g.subjects()])
    assert len(subjects) == 6, "There should be 6 subjects"
    expected_subjects = ["#event-1", "#event-2", "#place-1", "#place-2", "#offer-1", "#offer-2"]
    for s in expected_subjects:
        assert any([s in str(x) for x in subjects]), "{} expected to be among subjects".format(s)

    predicates = set([x for x in g.predicates()])
    assert len(predicates) == 7, "There should be 7 predicates"
    schema = rdflib.Namespace("http://schema.org/")
    expected_preds = [rdflib.RDF.type, schema.name, schema.startDate,
                      schema.location, schema.offers, schema.address, schema.url]
    for p in expected_preds:
        assert p in expected_preds, "{} expected to be among predicates"

    events = [x[0] for x in g.triples((None, rdflib.RDF.type, schema.MusicEvent))]
    assert len(events) == 2, "Expected 2 events"
    assert any(["#event-1" in str(e) for e in events])
    assert any(["#event-2" in str(e) for e in events])

    event_names = []
    for e in events:
        for x in g.triples((e, schema.name, None)):
            event_names.append(x[2])
    event_names = set(event_names)
    assert len(event_names) == 1, "There should be one unique event name"
    assert str(next(iter(event_names))) == "B.B. King", "The unique event name should be 'B.B. King'"

    start_date_data = [(x[0], x[2]) for x in g.triples((None, schema.startDate, None))]
    assert len(start_date_data) == 2, "There should be 2 start dates"
    for s in start_date_data:
        assert s[1].datatype == rdflib.XSD.dateTime, "start dates should be xsd:dateTime"
    events = [s[0] for s in start_date_data]
    assert any(["#event-1" in str(e) for e in events])
    assert any(["#event-2" in str(e) for e in events])

    location_data = [(x[0], x[2]) for x in g.triples((None, schema.location, None))]
    assert len(location_data) == 2, "There should be 2 locations"
    locations = [x[1] for x in location_data]
    assert any(["#place-1" in str(l) for l in locations])
    assert any(["#place-2" in str(l) for l in locations])
    events = [s[0] for s in location_data]
    assert any(["#event-1" in str(e) for e in events])
    assert any(["#event-2" in str(e) for e in events])

    offer_data = [(x[0], x[2]) for x in g.triples((None, schema.offers, None))]
    assert len(offer_data) == 2, "There should be 2 locations"
    offers = [x[1] for x in offer_data]
    assert any(["#offer-1" in str(l) for l in offers])
    assert any(["#offer-2" in str(l) for l in offers])
    events = [s[0] for s in offer_data]
    assert any(["#event-1" in str(e) for e in events])
    assert any(["#event-2" in str(e) for e in events])

    offers = [x for x in g.triples((None, rdflib.RDF.type, schema.Offer))]
    assert len(offers) == 2, "There should be 2 offers"
    assert any(["#offer-1" in str(e) for e in offers])
    assert any(["#offer-2" in str(e) for e in offers])

    urls = [x for x in g.triples((None, schema.url, None))]
    assert len(urls) == 2, "There should be 2 urls"
    for u in urls:
        assert u[2].datatype == rdflib.XSD.anyURI, "urls should be of type xsd:anyURI"

    places = [x for x in g.triples((None, rdflib.RDF.type, schema.Place))]
    assert len(places) == 2, "There should be 2 places"
    for p in places:
        assert len(list(g.triples((p[0], schema.name, None)))) == 1, "Place should have one name"
        assert len(list(g.triples((p[0], schema.address, None)))) == 1, "Place should have one address"
