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

""" Exceptions that pycsvw might raise """


class NoDefaultOrValueUrlError(Exception):
    """
    The exception thrown when a virtual column does not specify
    neither 'default' nor 'valueUrl'.
    """
    pass


class BothDefaultAndValueUrlError(Exception):
    """
    The exception thrown when a virtual column specifies both
    'default' and 'valueUrl'.
    """
    pass


class BothLangAndDatatypeError(Exception):
    """
    The exception when a literal ends up both with language and
     datatype which is not allowed.
    """
    pass


class RiotWarning(Warning):
    """
    The warning when riot call writes messages out to stderr.
    """
    pass


class RiotError(Exception):
    """
    The exception thrown from the call to riot
    """
    pass


class NullValueException(Exception):
    """
    Indicates to the caller that specified value is a null.
    """
    pass


class BothValueAndLiteralError(Exception):
    """
    The exception thrown when both 'value' and 'literal' are specified
    in an item in a list-valued 'valueUrl'.
    """
    pass


class BothValueAndDatatypeError(Exception):
    """
    The exception thrown when both 'value' and 'datatype' are specified
    in an item in a list-valued 'valueUrl'.
    """
    pass


class NoValueOrLiteralError(Exception):
    """
    The exception thrown when neither 'value' nor 'literal' is specified
    in an item in a list-valued 'valueUrl'.
    """
    pass


class InvalidItemError(Exception):
    """
    The exception thrown when an item in a list-valued 'valueUrl' is
    neither a string nor a dictionary.
    """
    pass


class MissingColumnError(KeyError):
    """
    The exception thrown when a column substitution fails to retrieve a column.
    """
    pass


class FailedSubstitutionError(Exception):
    """
    The exception thrown when a column substitution fails, see self.cause for underlying error.
    """

    def __init__(self, msg, cause, *args):
        super(FailedSubstitutionError, self).__init__(msg, *args)
        self.cause = cause
