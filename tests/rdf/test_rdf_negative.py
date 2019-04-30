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

from mock import patch

import pytest

import pycsvw
from pycsvw.csvw_exceptions import RiotError


@patch("pycsvw.csvw.Popen")
def test_riot_error(mock_popen):
    csvw = pycsvw.CSVW(csv_path="tests/simple.csv",
                       metadata_path="tests/simple.csv-metadata.json")
    mock_popen.return_value.communicate.return_value = (None, "myuniqueerror")
    mock_popen.returncode = -1

    with pytest.raises(RiotError) as exc:
        csvw.to_rdf()
    assert "myuniqueerror" in str(exc.value)


@patch("pycsvw.csvw.find_executable")
def test_riot_not_found_error(mock_find_executable):
    mock_find_executable.return_value = None
    csvw = pycsvw.CSVW(csv_path="tests/simple.csv",
                       metadata_path="tests/simple.csv-metadata.json")
    assert mock_find_executable.call_count == 0
    with pytest.raises(ValueError) as exc:
        csvw.to_rdf()
    assert "riot" in str(exc.value)
    assert mock_find_executable.call_count == 1


