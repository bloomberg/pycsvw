# pycsvw

Python implementation of a *variant* of the [W3C CSV on the Web specification](http://w3c.github.io/csvw/), primarily for
efficient RDF and JSON generation from a CSV file and its metadata. The supported variant of the recommendation has some additional features, mostly around specifying RDF to be an ordered container, and also some restrictions as listed below.

## Features:
1. Specify a cell to have a rdf:List-valued object. See [rdf:List valued objects for a cell](../master/docs/RdfListCell.md) for details.
2. For data types of time, date and dateTime, cell values that are recognized by [dateutil parser](https://dateutil.readthedocs.io/en/stable/parser.html) are accepted.

## Restrictions:
1. CSV metadata can be specified only through a separate JSON file.
2. Only minimal_mode is supported.
3. CSV file has to have a single header row.
4. The attribute "format" is ignored for any data type except "boolean". Value for any cell should be valid XSD value for XSD data types. However, for date, time and dateTime, values recognized by [dateutil parser](https://dateutil.readthedocs.io/en/stable/parser.html) are accepted.

All outputs are generated in UTF-8 encoding.

For implementation details, see [details](../master/docs/Implementation.md).
## Usage

```
$ pycsvw --help
Usage: pycsvw [OPTIONS]

  Command line interface for pycsvw.

Options:
  --csv-url TEXT        URL of the CSVW
  --csv-path TEXT       System path to the CSVW
  --metadata-url TEXT   URL of the CSVW metadata
  --metadata-path TEXT  System path to the CSVW metadata
  --json-dest TEXT      Destination of the JSON file to generate
  --rdf-dest TEXT...    Pair of format and destination path of RDF e.g.
                        'turtle out.ttl'
  --temp-dir TEXT       Use as the temporary folder for (intermediate) nt
                        serialization
  --riot-path TEXT      The path to the riot command e.g.
                        '/usr/bin/jena/bin/riot'
  --help                Show this message and exit.
```

## Example run

```
pycsvw --csv-path tests/examples/tree-ops-ext.csv --metadata-path tests/examples/tree-ops-ext.csv-metadata.json --rdf-dest turtle test.ttl
```
generates a `test.ttl` containing:
```
@prefix schema: <http://schema.org/> .
@prefix rr:    <http://www.w3.org/ns/r2rml#> .
@prefix grddl: <http://www.w3.org/2003/g/data-view#> .
@prefix wdr:   <http://www.w3.org/2007/05/powder#> .
@prefix duv:   <https://www.w3.org/TR/vocab-duv#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix xhv:   <http://www.w3.org/1999/xhtml/vocab#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix dqv:   <http://www.w3.org/ns/dqv#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rif:   <http://www.w3.org/2007/rif#> .
@prefix sd:    <http://www.w3.org/ns/sparql-service-description#> .
@prefix qb:    <http://purl.org/linked-data/cube#> .
@prefix oa:    <http://www.w3.org/ns/oa#> .
@prefix ma:    <http://www.w3.org/ns/ma-ont#> .
@prefix xml:   <http://www.w3.org/XML/1998/namespace> .
@prefix og:    <http://ogp.me/ns#> .
@prefix rdfa:  <http://www.w3.org/ns/rdfa#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dcat:  <http://www.w3.org/ns/dcat#> .
@prefix wrds:  <http://www.w3.org/2007/05/powder-s#> .
@prefix prov:  <http://www.w3.org/ns/prov#> .
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .
@prefix csvw:  <http://www.w3.org/ns/csvw#> .
@prefix sioc:  <http://rdfs.org/sioc/ns#> .
@prefix dctypes: <http://purl.org/dc/dcmitype/> .
@prefix cc:    <http://creativecommons.org/ns#> .
@prefix rev:   <http://purl.org/stuff/rev#> .
@prefix void:  <http://rdfs.org/ns/void#> .
@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .
@prefix org:   <http://www.w3.org/ns/org#> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
@prefix gr:    <http://purl.org/goodrelations/v1#> .
@prefix dc11:  <http://purl.org/dc/elements/1.1/> .
@prefix as:    <https://www.w3.org/ns/activitystreams#> .
@prefix ical:  <http://www.w3.org/2002/12/cal/icaltzd#> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix v:     <http://rdf.data-vocabulary.org/#> .
@prefix ldp:   <http://www.w3.org/ns/ldp#> .
@prefix ctag:  <http://commontag.org/ns#> .
@prefix dc:    <http://purl.org/dc/terms/> .

<http://example.org/tree-ops-ext#gid-6>
        <http://example.org/tree-ops-ext.csv#comments>
                " included bark" , "cavity or decay" , " trunk decay" , " root decay" , " codominant leaders" , " large leader or limb decay" , "  beware of BEES" , " previous failure root damage" ;
        <http://example.org/tree-ops-ext.csv#dbh>
                29 ;
        <http://example.org/tree-ops-ext.csv#inventory_date>
                "2010-06-01"^^xsd:date ;
        <http://example.org/tree-ops-ext.csv#kml>
                "<Point><coordinates>-122.156299,37.441151</coordinates></Point>"^^rdf:XMLLiteral ;
        <http://example.org/tree-ops-ext.csv#on_street>
                "ADDISON AV" ;
        <http://example.org/tree-ops-ext.csv#protected>
                true ;
        <http://example.org/tree-ops-ext.csv#species>
                "Robinia pseudoacacia" ;
        <http://example.org/tree-ops-ext.csv#trim_cycle>
                "Large Tree Routine Prune"@en .

<http://example.org/tree-ops-ext#gid-2>
        <http://example.org/tree-ops-ext.csv#dbh>
                11 ;
        <http://example.org/tree-ops-ext.csv#inventory_date>
                "2010-06-02"^^xsd:date ;
        <http://example.org/tree-ops-ext.csv#kml>
                "<Point><coordinates>-122.156749,37.440958</coordinates></Point>"^^rdf:XMLLiteral ;
        <http://example.org/tree-ops-ext.csv#on_street>
                "EMERSON ST" ;
        <http://example.org/tree-ops-ext.csv#protected>
                false ;
        <http://example.org/tree-ops-ext.csv#species>
                "Liquidambar styraciflua" ;
        <http://example.org/tree-ops-ext.csv#trim_cycle>
                "Large Tree Routine Prune"@en .

<http://example.org/tree-ops-ext#gid-1>
        <http://example.org/tree-ops-ext.csv#dbh>
                11 ;
        <http://example.org/tree-ops-ext.csv#inventory_date>
                "2010-10-18"^^xsd:date ;
        <http://example.org/tree-ops-ext.csv#kml>
                "<Point><coordinates>-122.156485,37.440963</coordinates></Point>"^^rdf:XMLLiteral ;
        <http://example.org/tree-ops-ext.csv#on_street>
                "ADDISON AV" ;
        <http://example.org/tree-ops-ext.csv#protected>
                false ;
        <http://example.org/tree-ops-ext.csv#species>
                "Celtis australis" ;
        <http://example.org/tree-ops-ext.csv#trim_cycle>
                "Large Tree Routine Prune"@en .
```


