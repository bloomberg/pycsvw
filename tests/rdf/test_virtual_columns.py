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

import pytest
from rdflib import ConjunctiveGraph, Literal
from rdflib.namespace import Namespace, XSD

from pycsvw import CSVW
from pycsvw.csvw_exceptions import NoDefaultOrValueUrlError, \
    BothDefaultAndValueUrlError, FailedSubstitutionError


def test_all_triples_with_row_numbers():
    csvw = CSVW(csv_path='tests/virtual1.csv',
                metadata_path='tests/virtual1.csv-metadata.json')
    rdf_output = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    all_subjects = {x for x in g.subjects()}
    assert len(all_subjects) == 4

    ns = Namespace("http://example.org/")
    assert ns['sub-1'] in all_subjects
    assert ns['sub-2'] in all_subjects
    assert len([g.triples((ns['sub-1'], ns['obj-1'], ns['pred-1']))]) == 1
    assert len([g.triples((ns['sub-2'], ns['obj-2'], ns['pred-2']))]) == 1


def test_default():
    csvw = CSVW(csv_path='tests/virtual1.csv',
                metadata_path='tests/virtual1.default.csv-metadata.json')
    rdf_output = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    all_subjects = {x for x in g.subjects()}
    assert len(all_subjects) == 4

    ns = Namespace("http://example.org/")
    assert ns['sub-1'] in all_subjects
    assert ns['sub-2'] in all_subjects
    assert len([g.triples((ns['sub-1'], ns['obj-1'], ns['myvalue']))]) == 1
    assert len([g.triples((ns['sub-2'], ns['obj-2'], ns['myvalue']))]) == 1


def test_table_level_about_url():
    csvw = CSVW(csv_path='tests/virtual1.csv',
                metadata_path='tests/virtual1.table.about_url.csv-metadata.json')
    rdf_output = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    all_subjects = {x for x in g.subjects()}
    assert len(all_subjects) == 2

    ns = Namespace("http://example.org/")
    assert ns['sub-1'] in all_subjects
    assert ns['sub-2'] in all_subjects
    assert len([g.triples((ns['sub-1'], ns['obj-1'], ns['myvalue']))]) == 1
    assert len([g.triples((ns['sub-2'], ns['obj-2'], ns['myvalue']))]) == 1


def test_default_with_datatype():
    csvw = CSVW(csv_path='tests/virtual1.csv',
                metadata_path='tests/virtual1.default.datatype.csv-metadata.json')
    rdf_output = csvw.to_rdf()
    g = ConjunctiveGraph()
    g.parse(data=rdf_output, format="turtle")

    ns = Namespace("http://example.org/")

    for x in [1, 2]:
        active_vals = list(g.triples((ns['sub-{}'.format(x)], ns['active'], None)))
        assert len(active_vals) == 1
        active_val = active_vals[0][2]
        assert isinstance(active_val, Literal)
        assert active_val.datatype == XSD.boolean
        assert active_val.value

        string_vals = list(g.triples((ns['sub-{}'.format(x)], ns['stringprop1'], None)))
        assert len(string_vals) == 1
        string_val = string_vals[0][2]
        assert isinstance(string_val, Literal)
        assert string_val.value == "some string"

        string_vals = list(g.triples((ns['sub-{}'.format(x)], ns['stringprop2'], None)))
        assert len(string_vals) == 1
        string_val = string_vals[0][2]
        assert isinstance(string_val, Literal)
        assert "%20" not in string_val.value


def test_negative_no_default_or_value():
    with pytest.raises(NoDefaultOrValueUrlError):
        print(CSVW(csv_path='tests/virtual1.csv',
                   metadata_path='tests/virtual1.NoDefaultOrValueUrlError.csv-metadata.json'))


def test_negative_both_default_or_value():
    with pytest.raises(BothDefaultAndValueUrlError):
        print(CSVW(csv_path='tests/virtual1.csv',
                   metadata_path='tests/virtual1.BothDefaultAndValueUrlError.csv-metadata.json'))


def test_negative_invalid_column():
    csvw = CSVW(csv_path='tests/virtual1.csv',
                metadata_path='tests/virtual1.negative2.csv-metadata.json')

    with pytest.raises(FailedSubstitutionError):
        print(csvw.to_rdf())
























