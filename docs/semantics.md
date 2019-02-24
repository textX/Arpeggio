# Semantic analysis - Visitors

This section explains how to transform parse tree to a more usable structure.

---

You will surely always want to extract some information from the parse tree or
to transform it in some more usable form.  The process of parse tree
transformation to other forms is referred to as *semantic analysis*.  You could
do that using parse tree navigation etc. but it is better to use some standard
mechanism.

In Arpeggio a visitor pattern is used for semantic analysis. You write a python
class that inherits `PTNodeVisitor` and has a methods of the form
`visit_<rule name>(self, node, children)` where rule name is a rule name from
the grammar.

    class CalcVisitor(PTNodeVisitor):

        def visit_number(self, node, children):
            return float(node.value)

        def visit_factor(self, node, children):
            if len(children) == 1:
                return children[0]
            sign = -1 if children[0] == '-' else 1
            return sign * children[-1]

        ...


During a semantic analysis a parse tree is walked in the depth-first manner and
for each node a proper visitor method is called to transform it to some other
form. The results are than fed to the parent node visitor method.  This is
repeated until the final, top level parse tree node is processed (its visitor is
called). The result of the top level node is the final output of the semantic
analysis.


To run semantic analysis apply your visitor class to the parse tree using
`visit_parse_tree` function.

```python
result = visit_parse_tree(parse_tree, CalcVisitor(debug=True))
```

The first parameter is a parse tree you get from the `parser.parse` call while
the second parameter is an instance of your visitor class. Semantic analysis can
be run in debug mode if you set `debug` parameter to `True` during visitor
construction. You can use this flag to print your own debug information from
visitor methods.

    class MyLanguageVisitor(PTNodeVisitor):

      def visit_somerule(self, node, children):
        if self.debug:
          print("Visiting some rule!")

During semantic analysis, each `visitor_xxx` method gets current parse tree node
as the `node` parameter and the evaluated children nodes as the `children`
parameter.

For example, if you have `expression` rule in your grammar than the
transformation of the non-terminal matched by this rule can be done as:

    def visitor_expression(self, node, children):
      ... # transform node using 'node' and 'children' parameter
      return transformed_node


`node` is the current `NonTerminal` or `Terminal` from the parse tree while the
`children` is an instance of `SemanticActionResults` class. This class is a
list-like structure that holds the results of semantic evaluation from the
children parse tree nodes (analysis is done bottom-up).

To suppress node completely return `None` from visitor method. In this case
the parent visitor method will not get this node in its `children` parameter.

In the [calc.py
example](https://github.com/textX/Arpeggio/blob/master/examples/calc/calc.py)
a semantic analysis
([CalcVisitor](https://github.com/textX/Arpeggio/blob/master/examples/calc/calc.py#L31)
class) will evaluate the result of arithmetic expression. The parse tree is thus
transformed to a single numeric value that represent the result of the
expression.

In the [robot.py
example](https://github.com/textX/Arpeggio/tree/master/examples/robot) a
semantic analysis
([RobotVisitor](https://github.com/textX/Arpeggio/blob/master/examples/robot/robot.py#L36)
class) will evaluate robot program (transform its parse tree) to the final robot
location.

Semantic analysis can do a complex stuff. For example, see
[peg_peg.py](https://github.com/textX/Arpeggio/blob/master/examples/peg_peg/peg_peg.py)
and
[PEGVisitor](https://github.com/textX/Arpeggio/blob/master/arpeggio/peg.py#L53)
class where the PEG parser for the given language is built using semantic
analysis.


## SemanticActionResults

Class of object returned from the parse tree nodes evaluation. Used for
filtering and navigation over evaluation results on children nodes.

Instance of this class is given as `children` parameter of `visitor_xxx`
methods.  This class inherits `list` so index access as well as iteration is
available.

Furthermore, child nodes can be filtered by rule name using attribute access.

```python
def visit_bar(self, node, children):
  # Index access
  child = children[2]

  # Iteration
  for child in children:
    ...

  # Returns a list of all rules created by PEG rule 'baz'
  baz_created = children.baz
```

## Post-processing in second calls

Visitor may define method with the `second_<rule_name>` name form. If this
method exists it will be called after all parse tree node are processed and it
will be given the results of the `visit_<rule_name>` call.

This is usually used when some additional post-processing is needed (e.g.
reference resolving).


## Default actions

For each parse tree node that does not have an appropriate `visit_xxx` method a
default action is performed. If the node is created by a plain string match
action will return `None` and thus suppress this node. This is handy for all
those syntax noise tokens (brackets, braces, keywords etc.).

For example, if your grammar is:

```python
number_in_brackets = "(" number ")"
number = r'\d+'
```

then the default action for `number` will return number node converted to
a string and the default action for `(` and `)` will return `None` and thus
suppress these nodes so the visitor method for `number_in_brackets` rule will
only see one child (from the `number` rule reference).

If the node is a non-terminal and there is only one child the default action
will return that child effectively passing it to the parent node visitor.

Default actions can be disabled by setting parameter `defaults` to `False` on
visitor construction.

```python
result = visit_parse_tree(parse_tree, CalcVisitor(defaults=False))
```

If you want to call this default behaviour from your visitor method call
`visit__default__(node, children)` on superclass (`PTNodeVisitor`).

```python
def visitor_myrule(self, node, children):
  if some_condition:
    ...
  else:
    return super(MyVisitor, self).visit__default__(node, children)
```

