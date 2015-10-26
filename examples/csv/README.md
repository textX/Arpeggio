# Comma-Separated Values (CSV) example

This is an example of a parser for a simple data interchange format - CSV
(Comma-Separated Values). CSV is a textual format for tabular data interchange.
It is described by RFC 4180.

`csv.py` file is an implementation using Python grammar specification.
`csv_peg.py` file is the same parser implemented using PEG grammar syntax where
the grammar is specified in the `csv.peg` file.

Run this examples:
```
$ python csv.py
$ python csv_peg.py
```

The output of both examples should be the same as the same file is parsed and
the same semantic analysis is used to extract data.

The full tutorial following this example can be found [here](http://igordejanovic.net/Arpeggio/tutorials/csv/)

