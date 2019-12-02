# JSON example

In this example a parser for [JSON format](http://json.org/) is built. 

`json.py` will load data from `test.json` file and build a [parse
tree](http://textx.github.io/Arpeggio/parse_trees/).

To run the example execute:

```bash
$ python json.py
```

This example will run in debug mode (setting `debug` is set to `True` in
`ParserPython` constructor call) detailed log is printed and `dot` files are
produced. `dot` files will be named based on the root grammar rule.

You can visualize `dot` files with some dot file viewers (e.g.
[ZGRViewer](http://zvtm.sourceforge.net/zgrviewer.html)) or produce graphics
with `dot` tool (you need to install [GraphViz](http://www.graphviz.org/) for
that)

```bash
$ dot -Tpng -O *dot
```
