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
from speed_test_csv import generate_csv_and_metadata, NUM_COLS


TRIPLES_SIZES = [20000, 30000, 50000, 100000, 200000, 300000, 500000, 1000000, 2000000]
FORMATS = ["turtle", "xml", "json-ld"]


for fmt in FORMATS:
    print "|Number of triples|pycsvw {fmt} (sec)|rdflib {fmt} (sec)|".format(fmt=fmt)
    for num_triples in TRIPLES_SIZES:
        generate_csv_and_metadata(num_triples)
        start = time.time()
        # Generate nt first for fairness to pycsvw
        csvw = CSVW(csv_path="csvfile.{}.csv".format(num_triples),
                    metadata_path="csvfile.{}.csv-metadata.json".format(num_triples))
        pycsvw_output = csvw.to_rdf(fmt)
        with open("{fmt}file.{num_t}.pycsvw.{fmt}".format(fmt=fmt, num_t=num_triples), "w") as out_file:
            out_file.write(pycsvw_output.encode("utf-8"))
        pycsvw_time = time.time() - start

        # Write the same contents into an nt-file using rdflib
        num_rows = int(num_triples) / NUM_COLS
        start = time.time()
        g = ConjunctiveGraph()
        for row in xrange(num_rows):
            for col in xrange(NUM_COLS):
                g.add((
                    URIRef("http://www.example.org/subjectrow{}col0".format(row)),
                    URIRef("http://www.example.org/predcolumn{}".format(col)),
                    Literal("row{}col{}".format(row, col))))
        g.serialize(destination="{fmt}file.{num_t}.rdflib.{fmt}".format(fmt=fmt, num_t=num_triples),
                    format=fmt)
        rdflib_time = time.time()-start
        print "|{}|{}|{}|".format(str(num_triples).rjust(len("Number of triples")),
                                  "{:.2f}".format(pycsvw_time).rjust(len("pycsvw  (sec)")+len(fmt)),
                                  "{:.2f}".format(rdflib_time).rjust(len("rdflib  (sec)")+len(fmt)))

