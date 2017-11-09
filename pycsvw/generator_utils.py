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

""" Generic utilities which might be necessary in future when we support JSON generation. """
import csv
import re

from dateutil.parser import parse
from six import PY2


XSD = "http://www.w3.org/2001/XMLSchema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
CSVW = "http://www.w3.org/ns/csvw#"
DATATYPE_MAP = {
    "anyAtomicType": XSD + "anyAtomicType",
    "anyURI": XSD + "anyURI",
    "base64Binary": XSD + "base64Binary",
    "boolean": XSD + "boolean",
    "date": XSD + "date",
    "dateTime": XSD + "dateTime",
    "dateTimeStamp": XSD + "dateTimeStamp",
    "decimal": XSD + "decimal",
    "integer": XSD + "integer",
    "long": XSD + "long",
    "int": XSD + "int",
    "short": XSD + "short",
    "byte": XSD + "byte",
    "nonNegativeInteger": XSD + "nonNegativeInteger",
    "positiveInteger": XSD + "positiveInteger",
    "unsignedLong": XSD + "unsignedLong",
    "unsignedInt": XSD + "unsignedInt",
    "unsignedShort": XSD + "unsignedShort",
    "unsignedByte": XSD + "unsignedByte",
    "nonPositiveInteger": XSD + "nonPositiveInteger",
    "negativeInteger": XSD + "negativeInteger",
    "double": XSD + "double",
    "duration": XSD + "duration",
    "dayTimeDuration": XSD + "dayTimeDuration",
    "yearMonthDuration": XSD + "yearMonthDuration",
    "float": XSD + "float",
    "gDay": XSD + "gDay",
    "gMonth": XSD + "gMonth",
    "gMonthDay": XSD + "gMonthDay",
    "gYear": XSD + "gYear",
    "gYearMonth": XSD + "gYearMonth",
    "hexBinary": XSD + "hexBinary",
    "QName": XSD + "QName",
    "normalizedString": XSD + "normalizedString",
    "token": XSD + "token",
    "language": XSD + "language",
    "Name": XSD + "Name",
    "NMTOKEN": XSD + "NMTOKEN",
    "xml": RDF + "XMLLiteral",
    "html": RDF + "HTML",
    "json": CSVW + "JSON",
    "time": XSD + "time",
    "string": XSD + "string",
    "enumeration": XSD + "enumeration"
}


def get_tz_suffix(tz_input):
    """Return the suffix to be added for time zone information."""
    if tz_input == "":
        return ""
    elif tz_input == "+0000":
        return "Z"

    # Add column between hour and date to make it work with XSD format
    return "{}:{}".format(tz_input[:3], tz_input[3:])


def parse_date(input_str):
    """Parse the specified date into xsd:date format."""
    if input_str.endswith("Z"):
        dt_obj = parse(input_str[:-1])
        return dt_obj.strftime("%Y-%m-%d") + "Z"

    tz_search = re.search(r"[\+-][\d]{2}:[\d]{2}$", input_str)
    if tz_search is None:
        dt_obj = parse(input_str)
        return dt_obj.strftime("%Y-%m-%d") + get_tz_suffix(dt_obj.strftime('%z'))

    tz_start_ind = tz_search.start()
    dt_obj = parse(input_str[:tz_start_ind])
    return dt_obj.strftime("%Y-%m-%d") + input_str[tz_start_ind:]


def parse_time(input_str):
    """Parse the specified time into xsd:time format."""
    dt_obj = parse(input_str)
    base = dt_obj.strftime('%H:%M:%S')
    # Handle microseconds, it is a single digit in XSD
    dt_ms = dt_obj.microsecond
    if dt_ms != 0:
        base += "{:.1f}".format(dt_ms/1000000.0)[1:]
    # Handle time zone
    return base + get_tz_suffix(dt_obj.strftime('%z'))


def parse_datetime(input_str):
    """Parse the specified dateTime into xsd:dateTime format."""
    return parse(input_str).isoformat()


def process_dates_times(value, base):
    """Entry function to process any date, time or dateTime."""
    out = ""
    if base == "date":
        out = parse_date(value)
    elif base == "time":
        out = parse_time(value)
    elif base == "dateTime":
        out = parse_datetime(value)

    return out


def read_csv(handle):
    """ Read CSV file
    :param handle: File-like object of the CSV file
    :return: csv.reader object
    """

    # These functions are to handle unicode in Python 2 as described in:
    # https://docs.python.org/2/library/csv.html#examples
    def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
        """ csv.py doesn't do Unicode; encode temporarily as UTF-8."""
        csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                                dialect=dialect, **kwargs)
        for row in csv_reader:
            # decode UTF-8 back to Unicode, cell by cell:
            yield [unicode(cell, 'utf-8') for cell in row]

    def utf_8_encoder(unicode_csv_data):
        """ Encode with UTF-8."""
        for line in unicode_csv_data:
            yield line.encode('utf-8')

    return unicode_csv_reader(handle) if PY2 else csv.reader(handle)
