# Comma-Separated Values (CSV) example

This is an example of a parser for a simple data interchange format - CSV
(Comma-Separated Values). CSV is a textual format for tabular data interchange.
It is described by RFC 4180.

`csv.py` file is an implementation using [Python grammar
specification](http://textx.github.io/Arpeggio/grammars/#grammars-written-in-python).
`csv_peg.py` file is the same parser implemented using [PEG grammar
syntax](http://textx.github.io/Arpeggio/grammars/#grammars-written-in-peg-notations)
where the grammar is specified in the `csv.peg` file.

Run this examples:
```
$ python csv.py
$ python csv_peg.py
```

The output of both examples should be the same as the same file is parsed and
the same semantic analysis is used to extract data.

The full tutorial following this example can be found [here](http://textx.github.io/Arpeggio/tutorials/csv/)

