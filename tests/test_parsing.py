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

from pycsvw.generator_utils import read_csv


def test_csv_parsing_quoted_newlines():
    csv_path = "tests/parsing.quoted_newlines.csv"
    csv_obj = io.open(csv_path, 'r', encoding='utf-8')
    csv_reader = read_csv(csv_obj)
    next(csv_reader)  # Ignore header
    rows = [row for row in csv_reader]
    assert len(rows) == 3, "3 rows are expected"
    for r in rows:
        assert len(r) == 3, "Each row is expected to have 3 cells"

    assert rows[0][0] == u'taxi'
    assert len(rows[0][1].splitlines()) == 2, "Row 1 cell 2 should have 2 lines"
    assert rows[0][2] == u' 30'

    assert rows[1][0] == u'multi-hop flight'
    assert len(rows[1][1].splitlines()) == 4, "Row 1 cell 2 should have 4 lines"
    assert rows[1][2] == u'1000'

    assert rows[2][0] == u'dinner'
    string = rows[2][1]
    assert u'\u2019' in string, "Expected to read unicode characters"
    assert rows[2][2] == u'100'


def test_csv_parsing_escapes_and_quotes():
    csv_path = "tests/parsing.escaped_quotes.csv"
    csv_obj = io.open(csv_path, 'r', encoding='utf-8')
    csv_reader = read_csv(csv_obj)
    next(csv_reader)  # Ignore header
    rows = [row for row in csv_reader]
    assert len(rows) == 4, "4q rows are expected"
    for r in rows:
        assert len(r) == 2, "Each row is expected to have 2 cells"
    assert rows[0][0] == u"taxi"
    assert rows[0][1] == u"go from x to y"
    assert rows[1][0] == u"quoted expense"
    assert rows[1][1] == u"for some reason it came with quotes in it"
    assert rows[2][0] == u"flight"
    assert rows[2][1] == u'had to fly "escaped quotes business" for this trip'
    assert rows[3][0] == u"car"
    assert rows[3][1] == u' some \ in it to be escaped'

