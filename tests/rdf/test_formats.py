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

import re
from itertools import dropwhile, takewhile
import tempfile
from mock import patch
import os
import stat

from six.moves import zip
import pytest
from rdflib import ConjunctiveGraph, Literal
from rdflib.namespace import Namespace, XSD

from pycsvw import CSVW


NUM_SUBJECTS = 4
NUM_TRIPLES_PER_SUBJ = 4


def verify_rdf_contents(contents, fmt):
    g = ConjunctiveGraph()
    g.parse(data=contents, format=fmt)

    books = Namespace('http://www.books.org/')
    isbn = Namespace("http://www.books.org/isbn/")

    # Check number of all triples
    assert sum(1 for _ in g.triples((None, None, None))) == NUM_SUBJECTS * NUM_TRIPLES_PER_SUBJ

    # Check number of subject
    subjs = set(g.subjects())
    expected_subjs = ["0062316095", "0374532508", "1610391845", "0374275637"]
    assert len(subjs) == len(expected_subjs)
    for s in expected_subjs:
        assert isbn[s] in subjs

        # Verify isbn number is positive integer
        s_isbn = list(g.triples((isbn[s], books['isbnnumber'], None)))
        assert len(s_isbn) == 1
        s_isbn_val = s_isbn[0][2]
        assert isinstance(s_isbn_val, Literal)
        assert s_isbn_val.datatype == XSD.positiveInteger
        # Verify pages is a unsignedShort
        s_page = list(g.triples((isbn[s], books['pagecount'], None)))
        assert len(s_page) == 1
        s_page_val = s_page[0][2]
        assert isinstance(s_page_val, Literal)
        assert s_page_val.datatype == XSD.unsignedShort
        # Verify hardcover is a boolean
        s_hardcover = list(g.triples((isbn[s], books['hardcover'], None)))
        assert len(s_hardcover) == 1
        s_hardcover_val = s_hardcover[0][2]
        assert isinstance(s_hardcover_val, Literal)
        assert s_hardcover_val.datatype == XSD.boolean
        # Verify price is a decimal
        s_price = list(g.triples((isbn[s], books['price'], None)))
        assert len(s_price) == 1
        s_price_val = s_price[0][2]
        assert isinstance(s_price_val, Literal)
        assert s_price_val.datatype == XSD.decimal


def validate_nt(contents):
    for line in contents.splitlines():
        # Verify that each line:
        # 1. Starts with books url followed by a 10-digit ISBN enclosed in <>
        # followed by single space
        # 2. Then continues with predicate that consists of book url followed by
        # a word which has 5 to 10 small letters and enclosed in <> followed by single space
        # 3. Then continues with a string enclosed in "" that has no escape characters
        # 4. Then continues with ^^ followed by a xsd url enclosed in <>
        # 5. and ends with a single space followed by a dot.
        pattern = r"<http://www.books.org/isbn/[0-9]{10}> " \
                  r"<http://www.books.org/[a-z]{5,10}> " \
                  r"\"[^\\]+\"\^\^<http://www.w3.org/2001/XMLSchema#[a-zA-Z]*> \."
        assert re.match(pattern, line)


def validate_turtle(contents):
    all_lines = contents.splitlines()
    # Separate prefixes from the body
    prefix_lines = [line for line in all_lines if line.startswith(u"@prefix")]
    prefixes = {
        "books": "http://www.books.org/",
        "isbn": "http://www.books.org/isbn/",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    }
    # Validate that specified prefixes are there
    for pre, url in prefixes.items():
        pattern = r"@prefix {}:[\s]* <{}> \.".format(pre, url)
        assert any([re.match(pattern, x) is not None for x in prefix_lines]), \
            "{} is not found among prefixes".format(pre)

    # Validate subject grouping
    # Move the cursor until the first subject
    iter = dropwhile(lambda x: len(x) == 0 or re.match("[\s]+$", x) or x.startswith(u"@prefix"), all_lines)
    # Check the block for each subject

    for s in range(NUM_SUBJECTS):
        this_sub_lines = list(takewhile(lambda x: len(x) != 0 and not re.match("[\s]+$", x), iter))
        assert len(this_sub_lines) == NUM_TRIPLES_PER_SUBJ
        # First line is where subject is defined
        subj_line = this_sub_lines[0]
        assert subj_line.startswith(u"isbn:")
        assert subj_line.endswith(";")
        # Rest of the lines starts with some whitespace
        assert all([re.match(r"^[\s]+", x) for x in this_sub_lines[1:]])
        # Next two lines end with ;
        assert all([x.endswith(u";") for x in this_sub_lines[1:(NUM_TRIPLES_PER_SUBJ-1)]])
        # Last line ends with a dot
        assert this_sub_lines[-1].endswith(u".")
        # Each line has a "books:" for the predicate
        assert all(["books:" in x for x in this_sub_lines])
        # One of the lines has true or false
        assert any(["true" in x or "false" in x for x in this_sub_lines])
        # Two of the lines has xsd:
        assert sum([1 for x in this_sub_lines if "xsd:" in x]) == 2


def validate_jsonld(contents):
    lines = contents.splitlines()
    assert lines[0] == "{"
    assert lines[-1] == "}"
    assert re.match(r'\s*"@graph"', lines[1])
    assert re.match(r'\s*"@id"', lines[2])


def validate_rdf_xml(contents):
    assert contents.startswith("<rdf:RDF")
    assert contents.endswith("</rdf:RDF>\n")
    lines = contents.splitlines()
    assert any([re.match(r"\s*<rdf:Description.*>", line) for line in lines])
    assert any([re.match(r"\s*</rdf:Description>", line) for line in lines])


TEST_PARAMS = [
    ("nt", validate_nt, "nt"),
    ("n3", validate_turtle, "n3"),
    ("turtle", validate_turtle, "turtle"),
    ("rdf", validate_rdf_xml, "xml"),
    ("rdf/xml", validate_rdf_xml, "xml"),
    ("json-ld", validate_jsonld, "json-ld")
]


# Each test case parametrizes:
# 1. Format input to the to_rdf method
# 2. Validation function for that format
# 3. The corresponding input value for rdflib.parse
@pytest.mark.parametrize("fmt, validate_func, rdflib_input", TEST_PARAMS)
def test_individual_formats(fmt, validate_func, rdflib_input):
    csvw = CSVW(csv_path="./tests/books.csv",
                metadata_path="./tests/books.csv-metadata.json")
    rdf_output = csvw.to_rdf(fmt=fmt)
    validate_func(rdf_output)
    verify_rdf_contents(rdf_output, rdflib_input)


@patch("pycsvw.csvw.find_executable")
def test_all_formats(mock_find_executable):
    mock_find_executable.return_value = True
    csvw = CSVW(csv_path="./tests/books.csv",
                metadata_path="./tests/books.csv-metadata.json")
    assert mock_find_executable.call_count == 0
    # Create file like objects
    input_val = []
    for f in TEST_PARAMS:
        input_val.append((tempfile.TemporaryFile(), f[0]))
    csvw.to_rdf_files(input_val)
    # Check each output
    for fmt in zip(input_val, TEST_PARAMS):
        file_obj = fmt[0][0]
        validate_func = fmt[1][1]
        rdflib_input = fmt[1][2]
        # Rewind and read
        file_obj.seek(0)
        contents = file_obj.read().decode('utf-8')
        # Validate
        validate_func(contents)
        verify_rdf_contents(contents, rdflib_input)

    assert mock_find_executable.call_count == 1


def test_tmp_files():
    tmp_dir = tempfile.mkdtemp(dir="/tmp")
    assert len(os.listdir(tmp_dir)) == 0
    csvw = CSVW(csv_path="./tests/books.csv",
                metadata_path="./tests/books.csv-metadata.json",
                temp_dir=tmp_dir)
    assert len(os.listdir(tmp_dir)) == 0

    csvw.to_rdf(fmt="nt")
    created_files = os.listdir(tmp_dir)
    assert len(created_files) == 1, "nt serialization should generate only 1 temp file"
    assert created_files[0].endswith(".nt")

    os.remove(os.path.join(tmp_dir, created_files[0]))
    assert len(os.listdir(tmp_dir)) == 0

    csvw.to_rdf(fmt="turtle")
    created_files = os.listdir(tmp_dir)
    assert len(created_files) == 2, "ttl serialization should generate two temps file"
    assert any([f.endswith(".nt") for f in created_files])
    assert any([f.endswith(".ttl") for f in created_files])
    # Check permissions
    expected_flags = [stat.S_IRUSR, stat.S_IRGRP, stat.S_IROTH]
    unexpected_flags = [stat.S_IWUSR, stat.S_IWGRP, stat.S_IWOTH]
    for f in created_files:
        st = os.stat(os.path.join(tmp_dir, f))
        for flag, non_flag in zip(expected_flags, unexpected_flags):
            assert bool(st.st_mode & flag)
            assert not bool(st.st_mode & non_flag)

    csvw.close()
    assert len(os.listdir(tmp_dir)) == 0


def test_context_mgr():
    tmp_dir = tempfile.mkdtemp(dir="/tmp")
    assert len(os.listdir(tmp_dir)) == 0

    with CSVW(csv_path="./tests/books.csv",
              metadata_path="./tests/books.csv-metadata.json",
              temp_dir=tmp_dir) as csvw:
        assert len(os.listdir(tmp_dir)) == 0

        csvw.to_rdf(fmt="nt")
        created_files = os.listdir(tmp_dir)
        assert len(created_files) == 1, "nt serialization should generate only 1 temp file"
        assert created_files[0].endswith(".nt")

        os.remove(os.path.join(tmp_dir, created_files[0]))
        assert len(os.listdir(tmp_dir)) == 0

        csvw.to_rdf(fmt="turtle")
        created_files = os.listdir(tmp_dir)
        assert len(created_files) == 2, "ttl serialization should generate two temps file"
        assert any([f.endswith(".nt") for f in created_files])
        assert any([f.endswith(".ttl") for f in created_files])

    assert len(os.listdir(tmp_dir)) == 0
