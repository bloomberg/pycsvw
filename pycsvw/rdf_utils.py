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

""" Utility functions used during rdf serialization."""
import re

from six.moves.urllib.parse import quote  # pylint: disable=import-error

from .csvw_exceptions import NullValueException, MissingColumnError, FailedSubstitutionError


SUB_PATTERN = re.compile(r'{(\w+)}')


def is_null_value(val, null_values):
    """Check if a val should be nulled out"""
    if null_values is None:
        return False
    return val in null_values


def resolve_url(url, prefixes):
    """Resolve the urls of form 'prefix:name'"""
    if ":" in url:
        prefix, _, tail = url.partition(":")
        if prefix in prefixes:
            return prefixes[prefix] + tail
    return url


def get_column_map(table_schema):
    """
    Return a map from column name to a tuple
    where the first element is the index and second is the spec
    """
    column_map = {}
    for ind, col in enumerate(table_schema["columns"]):
        if "name" in col:
            column_map[col["name"]] = (ind, col)
    return column_map


def apply_sub(url, row, column_name_to_sub, column_info, quote_sub=True):
    """ Apply a given substitution and raise if it is a null value. """
    try:
        column_ind, column_spec = column_info['column_map'][column_name_to_sub]
    except KeyError:
        raise MissingColumnError('Column {cn} not found in in column_map full map:\n{map}.'.format(cn=column_name_to_sub, map=column_info['column_map']))
    rep_after = row[column_ind]
    if is_null_value(rep_after, column_spec["null"]):
        raise NullValueException("'{}' is one of the null values specified")

    rep_before = "{" + column_name_to_sub + "}"
    if quote_sub:
        return url.replace(rep_before, quote(rep_after.encode('utf-8'), safe=':/'))
    else:
        return url.replace(rep_before, rep_after)


def apply_all_subs(url, row_num, row, column_info, quote_sub=True):
    """ Apply all substitutions (in format of {columnName}) and resolve the url """

    # Early return just with resolving if nothing to substitute
    if "{" not in url:
        return resolve_url(url, column_info['prefixes'])
    # Replace _row first
    out = url.replace('{_row}', row_num)
    # Extract pieces to sub from url
    subs = SUB_PATTERN.findall(out)
    for sub in subs:
        try:
            out = apply_sub(out, row, sub, column_info, quote_sub)
        except NullValueException:
            raise
        except Exception as e:
            raise FailedSubstitutionError('Unable to apply sub {sub} in url {url} row {num}'.format(
                sub=sub, url=url, num=row_num), e)
    return resolve_url(out, column_info['prefixes'])


def get_subject_for_cell(row_num, row, column_spec, table_about_url, shared_subject, column_info):
    """ Get the subject for the given cell."""
    if column_spec["aboutUrl"]:
        return apply_all_subs(column_spec["aboutUrl"], row_num, row, column_info)
    elif table_about_url:
        return apply_all_subs(table_about_url, row_num, row, column_info)

    return shared_subject


def get_predicate_for_cell(row_num, row, column_spec, table_ns, column_info):
    """ Get the predicate for the given cell."""
    if "propertyUrl" in column_spec:
        predicate = apply_all_subs(column_spec["propertyUrl"], row_num, row, column_info)
    elif "name" in column_spec:
        predicate = table_ns + "#" + column_spec["name"]
    else:
        predicate = table_ns + "#" + column_spec["titles"]
    return predicate
