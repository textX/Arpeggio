# Simple C-like language example

In this example a simple C-like language is parsed.

Program example is contained in `program.simple` file.

To run example do:

```bash
$ python simple.py
```

This example runs in debug mode (`debug` is `True` in `ParserPEG` constructor
call) and detailed log is printed and `dot` files are produced.  `dot` files
will be named based on the root grammar rule.

You can visualize `dot` files with some dot file viewers (e.g.
[ZGRViewer](http://zvtm.sourceforge.net/zgrviewer.html)) or produce graphics
with `dot` tool (you need to install [GraphViz](http://www.graphviz.org/) for that)

```bash
$ dot -Tpng -O *dot
```
