# Simple calculator example

This example demonstrates evaluation of simple expression consisting of numbers
and basic arithmetic operations (addition, subtraction, multiplication and
division).

`calc.py` defines grammar using [python
language](http://igordejanovic.net/Arpeggio/grammars/#grammars-written-in-python).

`calc_peg.py` shows the same example where grammar is specified using textual
[PEG
notation](http://igordejanovic.net/Arpeggio/grammars/#grammars-written-in-peg-notations)
(cleanpeg variant). The grammar is in `calc.peg` file.

Examples can be run with:

```bash
$ python calc.py
$ python calc_peg.py
```

Both grammar definition result in the same parser and the parsing end evaluation 
should produce the same result.

If run in debug mode (setting `debug` to `True` in `ParserPython` or `ParserPEG`
constructor call) detailed log is printed and `dot` files are produced.
`dot` files will be named based on the root grammar rule.

You can visualize `dot` files with some dot file viewers (e.g.
[ZGRViewer](http://zvtm.sourceforge.net/zgrviewer.html)) or produce graphics
with `dot` tool (you need to install [GraphViz](http://www.graphviz.org/) for that)

    dot -Tpng -O *dot

The full tutorial based on this example can be found
[here](http://igordejanovic.net/Arpeggio/tutorials/calc/).

