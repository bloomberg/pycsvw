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
This test covers the cases where csv file and metadata works with url safe characters like #, /, :
"""

from rdflib import ConjunctiveGraph, Literal, URIRef, Namespace

from pycsvw import CSVW

PRE_NS = Namespace('http://www.example.org/')


def test_url_safe_chars():

    csvw = CSVW(csv_path="tests/url_special_chars.csv",
                metadata_path="tests/url_special_chars.csv-metadata.json")
    rdf_output = csvw.to_rdf()

    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    # Check subjects
    sub1 = URIRef('http://www.example.org/c#1/chash2/chash3/chash4/chash5/chash6')
    literals = [Literal('c#1'), Literal('chash2'), Literal('chash3'),
                Literal('chash4'), Literal('chash6'), Literal('chash5')]
    verify_non_virtual_columns(sub1, g, literals)
    verify_virtual_columns(sub1, g, '#/:- _r1', '#/:-%20_r1')

    sub2 = URIRef('http://www.example.org/c/1/c/2/c/3/c/4/c/5/c/6')
    literals = [Literal('c/1'), Literal('c/2'), Literal('c/3'),
                Literal('c/4'), Literal('c/6'), Literal('c/5')]
    verify_non_virtual_columns(sub2, g, literals)
    verify_virtual_columns(sub2, g, '/#:- _r2','/#:-%20_r2')

    sub3 = URIRef('http://www.example.org/c:1/c:2/c:3/c:4/c:5/c:6')
    literals = [Literal('c:1'), Literal('c:2'), Literal('c:3'),
                Literal('c:4'), Literal('c:6'), Literal('c:5')]
    verify_non_virtual_columns(sub3, g, literals)
    verify_virtual_columns(sub3, g, ':#/-_ r3', ':#/-_%20r3')

    sub4 = URIRef('http://www.example.org/c-1/c-2/c-3/c-4/c-5/c-6')
    literals = [Literal('c-1'), Literal('c-2'), Literal('c-3'),
                Literal('c-4'), Literal('c-6'), Literal('c-5')]
    verify_non_virtual_columns(sub4, g, literals)
    verify_virtual_columns(sub4, g, '-/#_ :r4', '-/#_%20:r4')

    sub5 = URIRef('http://www.example.org/c%201/c%202/c%203/c%204/c%205/c%206')
    literals = [Literal('c 1'), Literal('c 2'), Literal('c 3'),
                Literal('c 4'), Literal('c 6'), Literal('c 5')]
    verify_non_virtual_columns(sub5, g, literals)
    verify_virtual_columns(sub5, g, ' -/#:_r5', '%20-/#:_r5')

    sub6 = URIRef('http://www.example.org/c_1/c_2/c_3/c_4/c_5/c_6')
    literals = [Literal('c_1'), Literal('c_2'), Literal('c_3'),
                Literal('c_4'), Literal('c_6'), Literal('c_5')]
    verify_non_virtual_columns(sub6, g, literals)
    verify_virtual_columns(sub6, g, '_ /:#r6', '_%20/:#r6')


def verify_virtual_columns(sub, g, orig_value_str, encoded_value_str):
    v1_triples = list(g.triples((sub, PRE_NS['v1p{}'.format(encoded_value_str)], None)))
    assert len(v1_triples) == 1
    assert "v1p{}".format(encoded_value_str) in str(v1_triples[0][1])
    assert orig_value_str == str(v1_triples[0][2])
    v2_triples = list(g.triples((sub, PRE_NS['v2p{}'.format(encoded_value_str)], None)))
    assert len(v2_triples) == 1
    assert "v2p{}".format(encoded_value_str) in str(v2_triples[0][1])
    assert 'v2v{}'.format(encoded_value_str) in str(v2_triples[0][2])

    # Standalone virtual column
    standalone_sub = URIRef('http://www.example.org/v3s{}'.format(encoded_value_str))
    v3_triples = list(g.triples((standalone_sub, None, None)))
    assert len(v3_triples) == 1
    assert "v3p{}".format(encoded_value_str) in str(v3_triples[0][1])
    assert 'v3v{}'.format(encoded_value_str) in str(v3_triples[0][2])


def verify_non_virtual_columns(sub, g, literals):
    all_triples = list(g.triples((sub, None, None)))
    assert len(all_triples) == 9
    assert (sub, PRE_NS['t#p'], literals[0]) in all_triples
    assert (sub, PRE_NS['t/p'], literals[1]) in all_triples
    assert (sub, PRE_NS['t:p'], literals[2]) in all_triples
    assert (sub, PRE_NS['t-p'], literals[3]) in all_triples
    assert (sub, PRE_NS['t_p'], literals[4]) in all_triples
    # Space value
    space_triple = list(g.triples((sub, PRE_NS['t%20p'], None)))
    assert len(space_triple) == 1
    assert "%20" in str(space_triple[0][1])
    assert " " not in str(space_triple[0][1])
    assert literals[5] == space_triple[0][2]








