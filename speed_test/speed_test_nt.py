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

import time

from rdflib import ConjunctiveGraph, URIRef, Literal

from pycsvw import CSVW
from speed_test_csv import NUM_COLS, generate_csv_and_metadata

TRIPLES_SIZES = [20000, 30000, 50000, 100000, 200000, 300000, 500000, 1000000, 2000000]

print "|Number of triples|pycsvw (sec)|rdflib (sec)|"
for num_triples in TRIPLES_SIZES:
    # Generate csv and its metadata
    generate_csv_and_metadata(num_triples)
    # Generate NT using pycsvw
    start = time.time()
    csvw = CSVW(csv_path="csvfile.{}.csv".format(num_triples),
                metadata_path="csvfile.{}.csv-metadata.json".format(num_triples))
    nt_output = csvw.to_rdf("nt")
    with open("ntfile.{}.pycsvw.nt".format(num_triples), "w") as nt_file:
        nt_file.write(nt_output.encode("utf-8"))
    pycsvw_nt_time = time.time() - start

    # Generate equivalent contents using rdflib
    num_rows = int(num_triples) / NUM_COLS
    start = time.time()
    g = ConjunctiveGraph()

    for row in xrange(num_rows):
        for col in xrange(NUM_COLS):
            g.add((
                URIRef("http://www.example.org/subjectrow{}col0".format(row)),
                URIRef("http://www.example.org/predcolumn{}".format(col)),
                Literal("row{}col{}".format(row, col))))
    g.serialize(destination="ntfile.{}.rdflib.nt".format(num_triples), format="nt")
    rdflib_nt_time = time.time()-start
    print "|{}|{}|{}|".format(str(num_triples).rjust(len("Number of triples")),
                            "{:.2f}".format(pycsvw_nt_time).rjust(len("pycsvw (sec)")),
                            "{:.2f}".format(rdflib_nt_time).rjust(len("rdflib (sec)")))

