# Implementation details and performance remarks

pycsvw internally always generates an [NT-serialization](https://www.w3.org/TR/n-triples/). If the requested
serialization is different than "NT", then it uses [riot](https://jena.apache.org/documentation/io/) from
[Apache Jena](https://jena.apache.org/index.html) to convert NT-serialization to the requested format.

The main reason why this approach was taken, instead of using [rdflib](https://rdflib.readthedocs.io/en/stable/)
is time and memory performance. As number of triples in the generated RDF serialization increase, time and memory
performance of riot (and thus pycsvw leveraging it) outperforms rdflib significantly. Below are some data that demonstrate
this. As it can be seen, it is an order of magnitude faster for any RDF serialization format as number of triples
get large, even though pycsvw has to parse CSV file and its metadata and take actions accordingly.

## Generating NT serialization with pycsvw vs using rdflib API
Below is the comparison of the time it takes to generate NT-serialization from csv file and its metadata
using pycsvw vs. the time it takes to generate the same content using rdflib API. The code that generated
this data can be found [here](../speed_test/speed_test_nt.py).

|Number of triples|pycsvw (sec)|rdflib (sec)|
|-----------------|------------|------------|
|            20000|        0.68|        2.08|
|            30000|        0.92|        3.22|
|            50000|        1.45|        5.29|
|           100000|        2.72|       10.83|
|           200000|        5.52|       22.50|
|           300000|        8.15|       33.86|
|           500000|       13.62|       56.72|
|          1000000|       28.63|      115.20|
|          2000000|       57.46|      231.88|

## Generating more complicated RDF serializations from NT
NT serialization is the most straightforward RDF serizalization. Other RDF serializations, such as
"turtle", "xml" and "json-ld" require more work during generation. Below is the comparison of the time it takes
to generate those serializations from csv file and its metadata using pycsvw vs. the time it takes to generate the same
content using rdflib API. The code that generated this data can be found [here](../speed_test/speed_test_other_formats.py).

### Turtle format

|Number of triples|pycsvw turtle (sec)|rdflib turtle (sec)|
|-----------------|-------------------|-------------------|
|            20000|               2.14|               5.51|
|            30000|               2.37|               8.26|
|            50000|               3.19|              14.14|
|           100000|               4.89|              28.25|
|           200000|               8.48|              57.70|
|           300000|              11.74|              86.21|
|           500000|              19.25|             145.28|
|          1000000|              36.80|             291.91|
|          2000000|              74.41|             593.95|

### RDF/XML format

|Number of triples|pycsvw xml (sec)|rdflib xml (sec)|
|-----------------|----------------|----------------|
|            20000|            2.38|            2.60|
|            30000|            2.82|            3.71|
|            50000|            3.47|            6.36|
|           100000|            5.43|           12.72|
|           200000|            9.41|           32.70|
|           300000|           13.25|           40.13|
|           500000|           21.79|           66.70|
|          1000000|           44.55|          134.53|
|          2000000|           86.31|          270.96|

### JSON-LD format

|Number of triples|pycsvw json-ld (sec)|rdflib json-ld (sec)|
|-----------------|--------------------|--------------------|
|            20000|                2.46|                5.43|
|            30000|                3.04|                8.20|
|            50000|                3.83|               13.30|
|           100000|                6.03|               27.00|
|           200000|               11.63|               62.68|
|           300000|               14.83|               85.25|
|           500000|               26.23|              142.42|
|          1000000|               54.65|              289.80|

