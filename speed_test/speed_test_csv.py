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

import csv
import json

NUM_COLS = 100


# Generate csv and its metadata for given triple size
def generate_csv_and_metadata(num_t):
    csv_file_name = "csvfile.{}.csv".format(num_t)
    with open(csv_file_name, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["column"+str(x) for x in xrange(NUM_COLS)])
        num_r = int(num_t) / NUM_COLS
        for i in xrange(num_r):
            csv_writer.writerow(["row{}col{}".format(i, x) for x in xrange(NUM_COLS)])
    # Write metadata
    metadata = {
        "@context": [
            "http://www.w3.org/ns/csvw",
            {
                "ns": "http://www.example.org/"
            }
        ],
        "url": csv_file_name,
        "tableSchema": {
          "aboutUrl": "http://www.example.org/subject{column0}",
          "columns": []
        }
    }
    for i in xrange(NUM_COLS):
        name = "column" + str(i)
        metadata["tableSchema"]["columns"].append({
            "name": name,
            "titles": name,
            "propertyUrl": "http://www.example.org/pred{}".format(name),
        })

    with open("{}-metadata.json".format(csv_file_name), "w") as json_file:
        json_file.write(json.dumps(metadata))
