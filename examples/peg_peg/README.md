# PEG in PEG example

This example demonstrates that PEG language can be defined in PEG.

In `peg.peg` file a grammar of PEG language is defined.  That grammar is loaded
and the parser is constructed using `ParserPEG` class from `arpeggio.peg`
module.

Semantic analysis in the form of `PEGVisitor` class is applied to the parse tree
produced from the `peg.peg` grammar. The result of the semantic analysis is
parser model which should be the same as the one that is used to parse the
`peg.peg` grammar in the first place.

To verify that, the parser model is replaced with the one produced by semantic
evaluation and the parsing of `peg.peg` is repeated.

To run the example do:

```bash
$ python peg_peg.py
```

This example runs in debug mode (setting `debug` to `True` in `ParserPEG`
constructor call) and detailed log is printed and `dot` files are produced.
`dot` files will be named based on the root grammar rule.

You can visualize `dot` files with some dot file viewers (e.g.
[ZGRViewer](http://zvtm.sourceforge.net/zgrviewer.html)) or produce graphics
with `dot` tool (you need to install [GraphViz](http://www.graphviz.org/) for that)

```bash
$ dot -Tpng -O *dot
```

You should verify that there is three parser model graphs and all the three are
the same:
- parser model produced by the canonical PEG grammar definition specified in
  `arpeggio.peg` module using [Python
  notation](http://igordejanovic.net/Arpeggio/grammars/#grammars-written-in-python).
- parser model produced by the `ParserPEG` construction that represent the
  grammar loaded from the `peg.peg` file.
- parser model created by applying `PEGVisitor` explicitly to the parse tree
  produced by parsing the `peg.peg` file.



