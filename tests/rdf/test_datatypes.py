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
This test covers all the datatypes in https://www.w3.org/TR/2015/REC-tabular-data-model-20151217/#datatypes
"""

from rdflib import ConjunctiveGraph, Literal, URIRef
from rdflib.namespace import XSD, Namespace, RDF
import pytest

from pycsvw import CSVW

NS = Namespace('https://www.example.org/')
CSVW_NS = Namespace("http://www.w3.org/ns/csvw#")


def test_time():

    with pytest.warns(None) as record:
        csvw = CSVW(csv_path="tests/datatypes.time.csv",
                    metadata_path="tests/datatypes.time.csv-metadata.json")
        rdf_output = csvw.to_rdf()

    assert len(record) == 0, "No warnings should be thrown, warning='{}' thrown".format(
        record[0].message)

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    NS = Namespace('https://www.example.org/')

    time1_lit = Literal("19:30:00", datatype=XSD.time)
    assert len(list(g.triples((NS['event/1'], NS['time1'], time1_lit)))) == 1

    time2_lit = Literal("09:30:10.5", datatype=XSD.time)
    assert len(list(g.triples((NS['event/1'], NS['time2'], time2_lit)))) == 1

    time3_lit = Literal("10:30:10Z", datatype=XSD.time)
    assert len(list(g.triples((NS['event/1'], NS['time3'], time3_lit)))) == 1

    time4_lit = Literal("11:30:10-06:00", datatype=XSD.time)
    assert len(list(g.triples((NS['event/1'], NS['time4'], time4_lit)))) == 1

    time5_lit = Literal("04:30:10+04:00", datatype=XSD.time)
    assert len(list(g.triples((NS['event/1'], NS['time5'], time5_lit)))) == 1


def test_date():

    with pytest.warns(None) as record:
        csvw = CSVW(csv_path="tests/datatypes.date.csv",
                    metadata_path="tests/datatypes.date.csv-metadata.json")
        rdf_output = csvw.to_rdf()

    assert len(record) == 0, "No warnings should be thrown, warning='{}' thrown".format(
        record[0].message)

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    date1_lit = Literal("2017-01-09", datatype=XSD.date)
    assert len(list(g.triples((NS['event/1'], NS['date1'], date1_lit)))) == 1

    date2_lit = Literal("2017-01-10Z", datatype=XSD.date)
    assert len(list(g.triples((NS['event/1'], NS['date2'], date2_lit)))) == 1

    date3_lit = Literal("2017-01-11", datatype=XSD.date)
    assert len(list(g.triples((NS['event/1'], NS['date3'], date3_lit)))) == 1

    date4_lit = Literal("2002-09-24-06:00", datatype=XSD.date)
    assert len(list(g.triples((NS['event/1'], NS['date4'], date4_lit)))) == 1

    date5_lit = Literal("2002-09-24+04:00", datatype=XSD.date)
    assert len(list(g.triples((NS['event/1'], NS['date5'], date5_lit)))) == 1


def test_datetime():
    with pytest.warns(None) as record:
        csvw = CSVW(csv_path="tests/datatypes.datetime.csv",
                    metadata_path="tests/datatypes.datetime.csv-metadata.json")
        rdf_output = csvw.to_rdf()

    assert len(record) == 0, "No warnings should be thrown, warning='{}' thrown".format(
        record[0].message)

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    dt1_lit = Literal("2002-05-30T09:00:00", datatype=XSD.dateTime)
    assert len(list(g.triples((NS['event/1'], NS['datetime1'], dt1_lit)))) == 1

    dt2_lit = Literal("2002-05-30T09:30:10.5", datatype=XSD.dateTime)
    assert len(list(g.triples((NS['event/1'], NS['datetime2'], dt2_lit)))) == 1

    dt3_lit = Literal("2002-05-30T09:30:10Z", datatype=XSD.dateTime)
    assert len(list(g.triples((NS['event/1'], NS['datetime3'], dt3_lit)))) == 1

    dt4_lit = Literal("2002-05-30T09:30:10-06:00", datatype=XSD.dateTime)
    assert len(list(g.triples((NS['event/1'], NS['datetime4'], dt4_lit)))) == 1

    dt5_lit = Literal("2002-05-30T09:30:10+04:00", datatype=XSD.dateTime)
    assert len(list(g.triples((NS['event/1'], NS['datetime5'], dt5_lit)))) == 1

    datestamp = Literal("2004-04-12T13:20:00-05:00", datatype=XSD.dateTimeStamp)
    assert len(list(g.triples((NS['event/1'], NS['datetimestamp'], datestamp)))) == 1


def test_others():
    with pytest.warns(None) as record:
        csvw = CSVW(csv_path="tests/datatypes.others.csv",
                    metadata_path="tests/datatypes.others.csv-metadata.json")
        rdf_output = csvw.to_rdf()

    assert len(record) == 0, "No warnings should be thrown, warning='{}' thrown".format(
        record[0].message)

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    triples_to_look_for = [
        (NS['custom_pred'], "someformatteddata", URIRef("https://www.datatypes.org#mycustomdatatypedefinition")),
        (NS["anyURI"], "https://www.sampleuri.org", XSD.anyURI),
        (NS["base64Binary"], "0FB8", XSD.base64Binary),
        (NS['boolean1'], True, XSD.boolean),
        (NS['boolean2'], False, XSD.boolean),
        (NS['boolean3'], True, XSD.boolean),
        (NS['boolean4'], False, XSD.boolean),
        (NS['integer'], -3, XSD.integer),
        (NS['long'], -1231235555, XSD.long),
        (NS['int'], 3, XSD.int),
        (NS['short'], -1231, XSD.short),
        (NS['byte'], 45, XSD.byte),
        (NS['nonNegativeInteger'], 111, XSD.nonNegativeInteger),
        (NS['positiveInteger'], 123456, XSD.positiveInteger),
        (NS['unsignedLong'], 3456, XSD.unsignedLong),
        (NS['unsignedInt'], 7890000, XSD.unsignedInt),
        (NS['unsignedShort'], 65000, XSD.unsignedShort),
        (NS['unsignedByte'], 254, XSD.unsignedByte),
        (NS['nonPositiveInteger'], -123, XSD.nonPositiveInteger),
        (NS['negativeInteger'], -34500000, XSD.negativeInteger),
        (NS['decimal'], "+3.5", XSD.decimal),
        (NS['double'], "4268.22752E11", XSD.double),
        (NS['float'], "+24.3e-3", XSD.float),
        (NS['duration'], "P2Y6M5DT12H35M30S", XSD.duration),
        (NS['dayTimeDuration'], "P1DT2H", XSD.dayTimeDuration),
        (NS['yearMonthDuration'], "P0Y20M", XSD.yearMonthDuration),
        (NS['gDay'], "---02", XSD.gDay),
        (NS['gMonth'], "--04", XSD.gMonth),
        (NS['gMonthDay'], "--04-12", XSD.gMonthDay),
        (NS['gYear'], "2004", XSD.gYear),
        (NS['gYearMonth'], "2004-04", XSD.gYearMonth),
        (NS['hexBinary'], "0FB8", XSD.hexBinary),
        (NS['QName'], "myElement", XSD.QName),
        (NS['normalizedString'], "This is a normalized string!", XSD.normalizedString),
        (NS['token'], "token", XSD.token),
        (NS['language'], "en", XSD.language),
        (NS['Name'], "_my.Element", XSD.Name),
        (NS['NMTOKEN'], "123_456", XSD.NMTOKEN),
        (NS['xml'], "<a>bla</a>", RDF.XMLLiteral),
        (NS['html'], "<div><p>xyz</p></div>", RDF.HTML),
        (NS['json'], "{}", CSVW_NS.JSON),

    ]
    for pred, lit_val, lit_type in triples_to_look_for:
        lit = Literal(lit_val, datatype=lit_type)
        assert len(list(g.triples((NS['event/1'], pred, lit)))) == 1, "Failed for {}".format(pred)
