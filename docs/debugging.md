# Debugging

When the stuff goes wrong you will want to debug your parser.

---

## Parser debug mode

During grammar design you can make syntax and semantic errors. Arpeggio will
report any syntax error with all the necessary information whether you are
building parser from python expressions or from a textual PEG notation.

For semantic error you have a debugging mode of operation which is entered by
setting `debug` parameter to `True` in the parser construction call. 

```python
parser = ParserPython(calc, debug=True)
```

When Arpeggio runs in debug mode it will print a detailed information of what it
is doing.

    >> Entering rule calc=Sequence at position 0 => *-(4-1)*5+(
      >> Entering rule OneOrMore in calc at position 0 => *-(4-1)*5+(
          >> Entering rule expression=Sequence in calc at position 0 => *-(4-1)*5+(
            >> Entering rule term=Sequence in expression at position 0 => *-(4-1)*5+(
                >> Entering rule factor=Sequence in term at position 0 => *-(4-1)*5+(
                  >> Entering rule Optional in factor at position 0 => *-(4-1)*5+(
                      >> Entering rule OrderedChoice in factor at position 0 => *-(4-1)*5+(
                        >> Match rule StrMatch(+) in factor at position 0 => *-(4-1)*5+(
                            -- No match '+' at 0 => '*-*(4-1)*5+('
                        >> Match rule StrMatch(-) in factor at position 0 => *-(4-1)*5+(
                            ++ Match '-' at 0 => '*-*(4-1)*5+('
                      << Leaving rule OrderedChoice
                  << Leaving rule Optional
                  >> Entering rule OrderedChoice in factor at position 1 => -*(4-1)*5+(2


## Visualization

Furthermore, while running in debug mode, a `dot` file (a graph description file
format from [GraphViz software
package](http://www.graphviz.org/content/dot-language)) representing _the parser
model_ will be created if the parser model is constructed without errors. 

This `dot` file can be rendered as image using one of available dot viewer
software or transformed to an image using `dot` tool
[GraphViz](http://graphviz.org/) software.

```bash
$ dot -Tpng -O calc_parser_model.dot
```

After this command you will get ``calc_parser_model.dot.png`` file which can be
opened in any ``png`` image viewer. This is how it looks like:

<a href="../images/calc_parser_model.dot.png" target="_blank"><img src="../images/calc_parser_model.dot.png" style="display:block; width: 15cm; margin-left:auto; margin-right:auto;"/></a>

Each node in this graph is a parsing expression.  Nodes are labeled by the type
name of the parsing expression.  If node represents the rule from the grammar,
the label is of the form `<rule_name>=<PEG type>` where `rule_name` is the
name of the grammar rule.  The edges connect children expressions. The labels on
the edges represent the order in which the graph will be traversed during
parsing.


Furthermore, if you parse some input while the parser is in debug mode, the
parse tree `dot` file will be generated also.

```python
parse_tree = parser.parse("-(4-1)*5+(2+4.67)+5.89/(.2+7)")
```
This `dot` file can also be converted to `png` with the command:

```bash
$ dot -Tpng -O calc_parse_tree.dot
```

Which produces `png` image given bellow.

<a href="../images/calc_parse_tree.dot.png" target="_blank"><img src="../images/calc_parse_tree.dot.png"/></a>

You can also explicitly render your parser model or parse tree to `dot` file
even if the parser is not in the debug mode.

For parser model this is achieved with the following Python code:

```python
from arpeggio.export import PMDOTExporter
PMDOTExporter().exportFile(parser.parser_model,
                            "my_parser_model.dot")
```

For parse tree it is achieved with:

```python
from arpeggio.export import PTDOTExporter
PTDOTExporter().exportFile(parse_tree,
                           "my_parse_tree.dot")
```

To get e.g. `png` images from `dot` files do as usual:

```bash
$ dot -Tpng -O *.dot
```


!!! note
    All tree images in this docs are rendered using Arpeggio's visualization and
    `dot` tool from the [GraphViz](http://graphviz.org/) software.

