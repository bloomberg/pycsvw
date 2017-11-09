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

""" RDF serialization in NT-format """
from uuid import uuid4

from six import string_types

from .generator_utils import process_dates_times, DATATYPE_MAP, read_csv
from .csvw_exceptions import NullValueException, BothValueAndLiteralError, \
    BothValueAndDatatypeError, NoValueOrLiteralError, InvalidItemError
from .rdf_utils import is_null_value, get_column_map, get_subject_for_cell, \
    get_predicate_for_cell, apply_all_subs


RDF_FIRST = "http://www.w3.org/1999/02/22-rdf-syntax-ns#first"
RDF_REST = "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest"
RDF_NIL = "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"
DATE_TIME_TYPES = ["date", "time", "dateTime"]


def create_literal(val, datatype=None, lang=None):
    """
    Put the value in unicode escaping new special characters to keep canonical form
    From NT specification at 'https://www.w3.org/TR/n-triples/#canonical-ntriples':
    "Within STRING_LITERAL_QUOTE, only the characters U+0022, U+005C, U+000A, U+000D are
    encoded using ECHAR. ECHAR must not be used for characters that are allowed directly
    in STRING_LITERAL_QUOTE."
    """

    escape_pairs = [(u'\u005C', r'\\'), (u'\u0022', r'\"'), (u"\u000A", r'\n'), (u"\u000D", r'\r')]
    for orig, rep in escape_pairs:
        val = val.replace(orig, rep)

    lit_value = u'"{}"'.format(val)

    if datatype is not None:
        lit_value += "^^<{}>".format(datatype)
    elif lang is not None:
        lit_value += "@{}".format(lang)
    return lit_value


def get_new_blank_node():
    """Get a blank node in canonical form."""
    return u"_:" + uuid4().hex.upper()


def write_objs_as_uri(output_obj, subject, predicate, raw_value):
    """Write object(s) for the column as a URI"""
    output_obj.write(u"<{}> <{}> <{}> .\n".format(
        subject, predicate, raw_value
    ).encode('utf-8'))


def write_objs_as_literal(output_obj, subject, predicate, raw_value, column_spec):
    """Write object(s) for the column as a literal"""
    is_empty_val = raw_value == ""
    datatype = column_spec["datatype"]
    is_dt_boolean = isinstance(datatype, dict) and datatype.get("base") == "boolean"
    if is_empty_val and not is_dt_boolean:
        # Empty values, in between two consecutive commas, are only allowed for boolean columns
        return

    if "separator" in column_spec:
        values = raw_value.split(column_spec["separator"])
    else:
        values = [raw_value]

    null_values = column_spec["null"]
    for value in values:
        # Check if it is a null value
        if is_null_value(value, null_values):
            continue

        kwargs = {}

        # Check if language is specified
        if "lang" in column_spec:
            kwargs["lang"] = column_spec["lang"]

        # Check if datatype is specified
        if datatype is not None:
            if isinstance(datatype, string_types):
                # Don't specify strings
                if datatype != "string":
                    kwargs["datatype"] = DATATYPE_MAP.get(datatype, datatype)

                    if datatype in DATE_TIME_TYPES:
                        value = process_dates_times(value, datatype)
            else:
                # Dictionary valued data type
                base = datatype["base"]
                kwargs["datatype"] = DATATYPE_MAP.get(base, base)
                if base == "boolean":
                    spec = datatype.get("format", None)
                    if spec is not None:
                        true_value = spec.split('|')[0]
                        value = "true" if value == true_value else "false"
                elif base in DATE_TIME_TYPES:
                    value = process_dates_times(value, base)

        lit_value = create_literal(value, kwargs.get("datatype"), kwargs.get("lang"))

        output_obj.write(u"<{}> <{}> {} .\n".format(
            subject, predicate, lit_value
        ).encode('utf-8'))


def write_obj_as_list(value_url, row_num, row, col, column_info,
                      subject, predicate, output):
    """Write the object as an RDF-list."""

    # valueUrl as a list, this will be an RDF collection
    items = []
    for val in value_url:
        if isinstance(val, string_types):
            items.append(apply_all_subs(val, row_num, row, column_info))
        elif isinstance(val, dict):
            if "requiredColumn" in val:
                # Check the required column value exists for this row
                req_value = row[column_info['column_map'][val['requiredColumn']][0]]
                if req_value == "":
                    continue

            if "value" in val:
                if "literal" in val:
                    raise BothValueAndLiteralError(
                        "'value' and 'literal' keys "
                        "co-exist in valueUrl of {}".format(col))
                if "datatype" in val:
                    raise BothValueAndDatatypeError(
                        "'value' and 'datatype' keys "
                        "co-exist valueUrl of {}".format(col))
                items.append(apply_all_subs(val["value"], row_num, row,
                                            column_info))
            else:
                if "literal" not in val:
                    raise NoValueOrLiteralError(
                        "Either 'value' or 'literal' key "
                        "should be provided in valueUrl of {}".format(col))
                lit_val = apply_all_subs(val["literal"], row_num, row, column_info)
                lit_dt = val["datatype"]
                lit_dt = DATATYPE_MAP[lit_dt] if lit_dt else lit_dt
                items.append((lit_val, {"datatype": lit_dt}))
        else:
            raise InvalidItemError("Items in valueUrl of {} should be "
                                   "either a string or dictionary".format(col))

    num_items = len(items)
    if num_items > 0:
        b_node = get_new_blank_node()
        output.write(u"<{}> <{}> {} .\n".format(
            subject, predicate, b_node
        ).encode('utf-8'))

        for ind, item in enumerate(items):
            # Get the value of the item
            if isinstance(item, string_types):
                output.write(u"{} <{}> <{}> .\n".format(
                    b_node, RDF_FIRST, item
                ).encode('utf-8'))
            else:
                lit_value, kwargs = item
                val = create_literal(lit_value,
                                     kwargs.get("datatype"),
                                     kwargs.get("lang"))
                output.write(u"{} <{}> {} .\n".format(
                    b_node, RDF_FIRST, val
                ).encode('utf-8'))

            if ind != (num_items - 1):
                # Still more items to come
                new_node = get_new_blank_node()
                output.write(u"{} <{}> {} .\n".format(
                    b_node, RDF_REST, new_node
                ).encode('utf-8'))
                b_node = new_node
            else:
                # Last item, finish with a nil
                output.write(u"{} <{}> <{}> .\n".format(
                    b_node, RDF_REST, RDF_NIL
                ).encode('utf-8'))


def write_row(output, row_num, row, table_info):
    """Write the NT-serialization for csv row."""
    table_schema = table_info['table_schema']
    column_info = table_info['column_info']
    table_about_url = table_schema["aboutUrl"]
    shared_subject = get_new_blank_node()

    for column_ind, col_value in enumerate(row):
        column_spec = table_schema["columns"][column_ind]
        if column_spec["suppressOutput"]:
            continue

        # Get the subject
        try:
            subject = get_subject_for_cell(row_num, row, column_spec, table_about_url,
                                           shared_subject, table_info['column_info'])
        except NullValueException:
            # null value, continue without adding this row
            continue

        # Get the predicate
        predicate = get_predicate_for_cell(row_num, row, column_spec,
                                           table_info['namespace'], table_info['column_info'])

        # Get objects
        if column_spec["valueUrl"] is not None:
            try:
                obj_val = apply_all_subs(column_spec["valueUrl"], row_num, row, column_info)
            except NullValueException:
                continue
            write_objs_as_uri(output, subject, predicate, obj_val)
        else:
            write_objs_as_literal(output, subject, predicate, col_value, column_spec)

    # Process virtual columns
    for column_spec in table_schema["columns"]:
        if not column_spec["virtual"]:
            continue

        # Get the subject
        if column_spec["aboutUrl"]:
            subject = apply_all_subs(column_spec["aboutUrl"], row_num, row, column_info)
        else:
            subject = apply_all_subs(table_about_url, row_num, row, column_info)
        # Get the predicate
        predicate = apply_all_subs(column_spec["propertyUrl"], row_num, row, column_info)
        # Get the objects
        if column_spec["valueUrl"]:
            value_url = column_spec["valueUrl"]

            if isinstance(value_url, list):
                write_obj_as_list(value_url, row_num, row, column_spec, column_info,
                                  subject, predicate, output)
            else:
                # Apply any substitution first
                obj_val = apply_all_subs(value_url, row_num, row, column_info)
                write_objs_as_uri(output, subject, predicate, obj_val)
        elif column_spec["default"]:
            # Apply any substitution first, but without quoting
            obj_val = apply_all_subs(column_spec["default"], row_num, row, column_info, False)
            write_objs_as_literal(output, subject, predicate, obj_val, column_spec)


def serialize(tables, md_tables, custom_prefixes, output_obj):
    """Serialize tables in NT-format."""

    for metadata in md_tables:
        # Bind table url
        table_url = metadata["url"]
        if metadata["suppressOutput"]:
            continue

        table_info = {
            'table_schema': metadata["tableSchema"],
            'namespace': table_url,
            'column_info': {
                'column_map': get_column_map(metadata["tableSchema"]),
                'prefixes': custom_prefixes
            }
        }
        # Read the csv file fresh after rewinding the file
        table_file_obj = tables[table_url]
        table_file_obj.seek(0)
        table_csv_reader = read_csv(table_file_obj)

        next(table_csv_reader)  # Ignore header

        for row_num, row in enumerate(table_csv_reader):
            write_row(output_obj, str(row_num + 1), row, table_info)
