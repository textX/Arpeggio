# Parse trees

Parse tree is a first structure you get from a successful parse.

---

Parse tree or concrete syntax tree is a tree structure built from the input
string during parsing.  It represent the structure of the input string. Each
node in the parse tree is either a [terminal](#terminal-nodes) or
[non-terminal](#non-terminal-nodes). Terminals are the leafs of the tree while
the inner nodes are non-terminals.

Here is an example parse tree for the `calc` grammar and the expression
`-(4-1)*5+(2+4.67)+5.89/(.2+7)`:

<a href="../images/calc_parse_tree.dot.png" target="_blank"><img src="../images/calc_parse_tree.dot.png"/></a>


Each non-leaf node is non-terminal. The name in this nodes are the names of the
grammar PEG rules that created them.

The leaf nodes are terminals and they are matched by the _string match_ or _regex
match_ rules.

In the square brackets is the location in the input stream where the
terminal/non-terminal is recognized.

Each parse tree node has the following attributes:

- **rule** - the parsing expression that created this node.
- **rule_name** - the name of the rule if it was the root rule or empty string
  otherwise.
- **position** - the position in the input stream where this node was
  recognized.
- **position_end** - the end of the node in the input stream. This index is one
  char behind the last char that belongs to this node. Thus, `position_end -
  position == length of the node`.

If you want to get line and column from position you can use `pos_to_linecol`
parser method.

```python
  line, col = parser.pos_to_linecol(node.position)
```


## Terminal nodes

Terminals in Arpeggio are created by the specializations of the parsing
expression `Match` class.  There are two specialization of `Match` class:

- `StrMatch` if the literal string is matched from the input or
- `RegExMatch` if a regular expression is used to match input.

To get the matched string from the terminal object just convert it to string
(e.g. `str(t)` where `t` is of `Terminal` type).


## Non-terminal nodes

Non-terminal nodes are non-leaf nodes of the parse tree. They are created by PEG
grammar rules.  Children of non-terminals can be other non-terminals or
terminals.

For example, nodes with the labels `expression`, `factor` and `term` from
the above parse tree are non-terminal nodes created by the rules with the same
names.

`NonTerminal` inherits from `list`. The elements of `NonTerminal` are its
children nodes.  So, you can use index access:

```python
child = pt_node[2]
```

Or iteration:

```python
for child in pt_node:
  ...
```

Additionally, you can access children by the child rule name:

For example:

```python
# Grammar
def foo(): return "a", bar, "b", baz, "c", ZeroOrMore(bar)
def bar(): return "bar"
def baz(): return "baz"

# Parsing
parser = ParserPython(foo)
result = parser.parse("a bar b baz c bar bar bar")

# Accessing parse tree nodes. All asserts will pass.
# Index access
assert result[1].rule_name  == 'bar'
# Access by rule name
assert result.bar.rule_name == 'bar'

# There are 8 children nodes of the root 'result' node.
# Each child is a terminal in this case.
assert len(result) == 8

# There is 4 bar matched from result (at the beginning and from ZeroOrMore)
# Dot access collect all NTs from the given path
assert len(result.bar) == 4
# You could call dot access recursively, e.g. result.bar.baz if the
# rule bar called baz. In that case all bars would be collected from
# the root and for each bar all baz will be collected.

# Verify position
# First 'bar' is at position 2 and second is at position 14
assert result.bar[0].position == 2
assert result.bar[1].position == 14

```


## Parse tree reduction

Parser can be configured to create a reduced parse tree. More information can be
found [here](configuration.md#parse-tree-reduction).

