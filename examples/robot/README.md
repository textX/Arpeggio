# Robot example

In this example a parser for simple language for robot control is demonstrated.

`robot.py` will instantiate a parser for [grammar defined using
Python](http://textx.github.io/Arpeggio/grammars/#grammars-written-in-python).
`robot_peg.py` is the same parser but constructed using a [PEG
grammar](http://textx.github.io/Arpeggio/grammars/#grammars-written-in-peg-notations)
defined in file `robot.peg`.

This example demonstrates how to interpret the program on robot language using
semantic analysis. During analysis a position of the robot will be updated.
At the end of the analysis a final position is returned.

To run examples:

```bash
$ python robot.py
$ python robot_peg.py
```

Both examples must produce the same result.

This example will run in debug mode (`debug` is set to `True` in `ParserPython`
constructor call) detailed log is printed and `dot` files are produced. `dot`
files will be named based on the root grammar rule.

You can visualize `dot` files with some dot file viewers (e.g.
[ZGRViewer](http://zvtm.sourceforge.net/zgrviewer.html)) or produce graphics
with `dot` tool (you need to install [GraphViz](http://www.graphviz.org/) for
that)

```bash
$ dot -Tpng -O *dot
```

