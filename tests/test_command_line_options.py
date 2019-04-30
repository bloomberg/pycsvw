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

from builtins import str as text

from click.testing import CliRunner
from mock import patch, Mock

from pycsvw.csvw import CSVW
from pycsvw.scripts.cli import main


def test_main_using_paths():

    csv_path = "tests/simple.csv"
    metadata_path = "tests/simple.csv-metadata.json"

    runner = CliRunner()

    with patch.object(CSVW, "to_rdf") as rdf_mocked, patch.object(CSVW, "to_json") as json_mocked:
        rdf_mocked.return_value = "some ttl contents"
        json_mocked.return_value = "some json"
        result = runner.invoke(main, ["--csv-path", csv_path,
                                      "--metadata-path", metadata_path,
                                      "--rdf-dest", "turtle", "/dev/null"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["--csv-path", csv_path,
                                      "--metadata-path", metadata_path,
                                      "--json-dest", "/dev/null"])
        assert result.exit_code == 0


@patch("pycsvw.csvw.urlopen")
def test_main_using_urls(mock_urlopen):

    metadata_path = "tests/simple.csv-metadata.json"
    metadata_url = "http://example.org/simple.metadata"
    csv_url = "http://example.org/simple.csv"
    csv_path = "tests/simple.csv"

    with open(csv_path, 'r') as csv_file:
        csv_contents = text(csv_file.read())
    with open(metadata_path, 'r') as metadata_file:
        metadata_contents = text(metadata_file.read())

    reader = Mock()
    reader.read.side_effect = [csv_contents, metadata_contents]
    mock_urlopen.return_value = reader

    runner = CliRunner()

    with patch.object(CSVW, "to_rdf") as rdf_mocked, patch.object(CSVW, "to_json") as json_mocked:
        rdf_mocked.return_value = "some ttl contents"
        json_mocked.return_value = "some json"
        result = runner.invoke(main, ["--csv-url", csv_url,
                                      "--metadata-path", metadata_path,
                                      "--rdf-dest", "turtle", "/dev/null"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["--csv-path", csv_path,
                                      "--metadata-url", metadata_url,
                                      "--rdf-dest", "turtle", "/dev/null"])
        assert result.exit_code == 0










