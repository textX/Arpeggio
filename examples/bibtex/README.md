# BibTeX example

This example demonstrates building parser for a [BibTeX](http://www.bibtex.org/)
format, a format for used to describe bibliographic references.

`bibtex_example.bib` file contains several BibTeX entries. This file is parsed
with the parser specified in `bibtex.py` and transformed to Python structure.

`bibtex.py` example accepts one parameter from the command line. That parameter
represents a BibTeX input file.

To run this example execute:

```bash
$ python bibtex.py bibtex_example.bib
```

Read [the full tutorial](http://textx.github.io/Arpeggio/tutorials/bibtex/)
following this example.

