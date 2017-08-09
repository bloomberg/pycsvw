# Generating rdf:Lists using CSVW

An [rdf:List](https://www.w3.org/TR/rdf-schema/#ch_list) is an ordered container.
CSVW specification itself does not allow specification of generation of rdf:Lists
using contents of one or more cells. As explained [here](https://www.w3.org/TR/2016/NOTE-csvw-ucr-20160225/#p-acc-req),
this was one of the use cases that did not make it into the specification.

We added additional support for users to be able to indicate rdf:List generation, possibly as a mixture of
Literals and IRIs and with different datatypes for literal, and conditionally on the existence of
specified data in the column. If the `valueUrl` in the metadata is a list, each item in the list can be
either directly a string (which will be used as a string literal) or a dictionary with keys `value` or `literal`
 (to indicate IRI vs literal) and optionally `requiredColumn` (to indicate the necessary column value to exist
 for that list item to be generated) and `datatype` (to indicate the datatype in the case of `literal`).

## Example:

Assume that you have the following csv-file with columns `element`, `definition`, `type`, `maxlen`, `minlen`:

```
element,definition,type,maxlen,minlen
amount,the amount paid,decimal,10,1
description,description of the expense,string,100,
id,transaction id,integer,,0
```

If you have the following virtual columns defined in your metadata file:

```
{
"aboutUrl": "http://example.org/element/{element}-RANGE",
"virtual": true,
"propertyUrl": "owl:onDatatype",
"valueUrl": "xsd:{type}"
},
{
"virtual": true,
"aboutUrl": "http://example.org/element/{element}-RANGE",
"propertyUrl": "owl:withRestrictions",
"valueUrl": [
  "xsd:{type}",
  {
    "value": "xsd:MaxLength",
    "requiredColumn": "maxlen"
  },
  {
    "literal": "{maxlen}",
    "datatype": "nonNegativeInteger",
    "requiredColumn": "maxlen"
  },
  {
    "value": "xsd:MinLength",
    "requiredColumn": "minlen"
  },
  {
    "literal": "{minlen}",
    "datatype": "nonNegativeInteger",
    "requiredColumn": "minlen"
  }
]
}
```

then the following triples are generated in the turtle serialization:

```
<http://example.org/element/amount-RANGE>
        owl:onDatatype        xsd:decimal ;
        owl:withRestrictions  ( xsd:decimal xsd:MaxLength "10"^^xsd:nonNegativeInteger xsd:MinLength "1"^^xsd:nonNegativeInteger ) .

<http://example.org/element/description-RANGE>
        owl:onDatatype        xsd:string ;
        owl:withRestrictions  ( xsd:string xsd:MaxLength "100"^^xsd:nonNegativeInteger ) .

<http://example.org/element/id-RANGE>
        owl:onDatatype        xsd:integer ;
        owl:withRestrictions  ( xsd:integer xsd:MinLength "0"^^xsd:nonNegativeInteger ) .
```

Notice that the list generated for the first row for has all the list elements whereas the row for
`description` only has `maxLength` (lacking `minLength`) and the row for `id` only has `minLength` (lacking
`maxLength`).










