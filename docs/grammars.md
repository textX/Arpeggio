# Grammars

With grammar you teach Arpeggio how to parse your inputs.


---

Arpeggio is based
on [PEG grammars](https://en.wikipedia.org/wiki/Parsing_expression_grammar). PEG
is a type of formal grammar that is given as a set of rules for recognizing
strings of the language. In a way it is similar to context-free grammars with a
very important distinction that PEG are always unambiguous. This is achieved by
making choice operator ordered. In PEGs a first choice from left to right that
matches will be used.

!!! note
    More information on PEGs can be found on [this page](http://bford.info/packrat/).

PEG grammar is a set of PEG rules. PEG rules consists of parsing expressions and
can reference (call) each other.

Example grammar in PEG notation:

    first = 'foo' second+ EOF
    second = 'bar' / 'baz'

In this example `first` is the root rule. This rule will match a literal string
`foo` followed by one or more `second` rule (this is a rule reference) followed
by end of input (`EOF`). `second` rule is ordered choice and will match either
`bar` or `baz` in that order.

!!! warning
    Arpeggio requires `EOF` rule/anchor at the end of the root rule if you
    want the whole input to be consumed. If you leave out `EOF` Arpeggio will
    parse as far as it can, leaving the rest of the input unprocessed, and return
    without an error. So, be sure to always end your root rule sequence with
    `EOF` if you want a complete parse.


During parsing each successfully matched rule will create a parse tree node. At
the end of parsing a complete [parse tree](parse_trees.md) of the input will be
returned.

In Arpeggio each PEG rule consists of atomic parsing expression which can be:

- **terminal match rules** - create
  a [Terminal nodes](parse_trees.md#terminal-nodes):
    - **String match** - a simple string that is matched literally from the
      input string.
    - **RegEx match** - regular expression match (based on python `re` module).

- **non-terminal match rules** - create
  a [Non-terminal nodes](parse_trees.md#non-terminal-nodes):
    - **Sequence** - succeeds if all parsing expressions matches at current
      location in the defined order. Matched input is consumed.
    - **Ordered choice** - succeeds if any of the given expressions matches at
      the current location. The match is tried in the order defined. Matched
      input is consumed.
    - **Zero or more** - given expression is matched until match is successful.
      Always succeeds. Matched input is consumed.
    - **One or more** - given expressions is matched until match is successful.
      Succeeds if at least one match is done. Matched input is consumed.
    - **Optional** - matches given expression but will not fail if match can't be
      done. Matched input is consumed.
    - **Unordered group** - matches given expressions in any order. Each given
      expression must be matched exactly once. Expressions are repeatedly tried
      from left to right until any succeeds, the process is repeated ignoring
      already matched expressions, thus the behavior is deterministic. Matched
      input is consumed.
    - **And predicate** - succeeds if given expression matches at current
      location but does not consume any input.
    - **Not predicate** - succeeds if given expression **does not** match at
      current location but does not consume any input.

PEG grammars in Arpeggio may be written twofold:

- Using Python statements and expressions.
- Using textual PEG syntax (currently there are two variants, see below).


## Grammars written in Python

Canonical form of grammar specification uses Python statements and expressions.

Here is an example of arpeggio grammar for simple calculator:

    def number():     return _(r'\d*\.\d*|\d+')
    def factor():     return Optional(["+","-"]), [number,
                              ("(", expression, ")")]
    def term():       return factor, ZeroOrMore(["*","/"], factor)
    def expression(): return term, ZeroOrMore(["+", "-"], term)
    def calc():       return OneOrMore(expression), EOF

Each rule is given in the form of Python function. Python function returns data
structure that maps to PEG expressions and state statements.

- **Sequence** is represented as Python tuple.
- **Ordered choice** is represented as Python list where each element is one
  alternative.
- **One or more** is represented as an instance of `OneOrMore` class.
  The parameters are treated as a containing sequence.
- **Zero or more** is represented as an instance of `ZeroOrMore` class.
  The parameters are treated as a containing sequence.
- **Optional** is represented as an instance of `Optional` class.
- **Unordered group** is represented as an instance of `UnorderedGroup` class.
- **And predicate** is represented as an instance of `And` class.
- **Not predicate** is represented as an instance of `Not` class.
- **Literal string match** is represented as string or regular expression given
  as an instance of `RegExMatch` class.
- **Match state predicate** is represented as an instance of `MatchState` class.
  A parsing state passed to the instance must be of `ParsingState` class.
  The class checks if the current state is the same as the provided one.
- **Push state command** is represented as an instance of `PushState` class.
  A parsing state passed to the instance must be of `ParsingState` class.
- **Pop state predicate** is represented as an instance of `PopState` class.
  A parsing state passed to the instance must be of `ParsingState` class.
  The class checks if the current state is the same as the provided one if any.
- **State layer wrapper** is represented as an instance of
  `StateLayerWrapper` class. This wrapper is used to isolate the state
  of a specific group of rules and check its integrity.
- **End of string/file** is recognized by the `EOF` special rule.

For example, the `calc` language consists of one or more `expression` and
end of file.

`factor` rule consists of optional `+` or `-` char matched in that order
(they are given in Python list thus ordered choice) followed by the ordered
choice of `number` rule and a sequence of `expression` rule in brackets.
This rule will match an optional sign (`+` or `-` tried in that order) after
which follows a `number` or an `expression` in brackets (tried in that
order).

From this description Arpeggio builds **the parser model**. Parser model is a
graph of parser expressions (see [Grammar
visualization](debugging.md#visualization)).  Each node of the graph is
an instance of some of the classes described above which inherits
`ParserExpression`.

Parser model construction is done during parser instantiation. For example, to
instantiate `calc` parser you do the following:

```python
parser = ParserPython(calc)
```

Where `calc` is the function defining the root rule of your grammar. There is no
code generation. Parser works as an interpreter for your grammar. The grammar is
used to configure Arpeggio parser to recognize your language (in this case the
`calc` language). In other words, Arpeggio interprets the parser model (your
grammar).

After parser construction your can call `parser.parse` to parse your input text.

```python
input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"
parse_tree = parser.parse(input_expr)
```

Arpeggio will start from the root node and traverse _the parser model graph_
consuming all matched input. When all root node branches are traversed the
parsing is done and _the parse tree_ is returned.

You can navigate and analyze parse tree or transform it using visitor pattern to
some more usable form (see [Semantic analysis - Visitors](semantics.md#visitors))


### Overriding of special rule classes

As we noted above some parsing rules are mapped to Python types (`Sequence` to
a tuple, `OrderedChoice` to a list and `StrMatch` to a string). Sometimes it is
useful to override classes that will be instantiated by Arpeggio to provide
altered behavior.

For example, if we want to [suppress all string
matches](parse_trees.md#suppressing-parse-tree-nodes) we can register our version
of `StrMatch` which sets `suppress` to `True`:

```python
class SuppressStrMatch(StrMatch):
    suppress = True

def grammar():
    return "one", "two", RegExMatch(r'\d+'), "three"

parser = ParserPython(grammar,
                      syntax_classes={'StrMatch': SuppressStrMatch})

result = parser.parse("one two 42 three")

# Only regex will end up in the tree
assert len(result) == 1
assert result[0] == "42"

```

We use `syntax_classes` parameter to `ParserPython` of `dict` type where keys
are names of the original classes and values are our modified class. Now,
Arpeggio will instantiate our class whenever it encounters Python string in the
grammar.

This feature is, obviously, only available for grammars written in Python.


## Grammars written in PEG notations

Grammars can also be specified using PEG notation. There are actually two of
them at the moment and both notations are implemented using canonical Python
based grammars (see
modules
[arpeggio.peg](https://github.com/textX/Arpeggio/blob/master/arpeggio/peg.py) and
[arpeggio.cleanpeg](https://github.com/textX/Arpeggio/blob/master/arpeggio/cleanpeg.py)).

There are no significant differences between those two syntax. The first one use
more traditional approach using `<-` for rule assignment and `;` for the rule
terminator. The second syntax (from `arpeggio.cleanpeg`) uses `=` for assignment
and does not use rule terminator. Which one you choose is totally up to you. If
your don't like any of these syntaxes you can make your own (look at
`arpeggio.peg` and `arpeggio.cleanpeg` modules as an example).

An example of the `calc` grammar given in PEG syntax (`arpeggio.cleanpeg`):

```python
number = r'\d*\.\d*|\d+'
factor = ("+" / "-")? (number / "(" expression ")")
term = factor (( "*" / "/") factor)*
expression = term (("+" / "-") term)*
calc = expression+ EOF
```

Each grammar rule is given as an assignment where the LHS is the rule name (e.g.
`number`) and the RHS is a PEG expression.

- **Literal string matches** are given as strings (e.g. `"+"`).
- **Regex matches** are given as strings with prefix `r` (e.g.
  `r'\d*\.\d*|\d+'`).
- **Sequence** is a space separated list of expressions (e.g. `expression+
  EOF` is a sequence of two expressions).
- **Ordered choice** is a list of expression separated with `/` (e.g. `"+" /
  "-"`).
- **Optional** expression is specified by `?`operator (e.g. `expression?`) and
  matches zero or one occurrence of *expression*
- **Zero or more** expression is specified by `*` operator (e.g. `(( "*" /
  "/" ) factor)*`).
- **One of more** is specified by `+` operator (e.g. `expression+`).
- **Unordered group** is specified by `#` operator (e.g. `sequence#`). It has
  sense only if applied to the sequence expression. Elements of the sequence are
  matched in any order.
- **And predicate** is specified by `&` operator (e.g. `&expression` - not
  used in the grammar above).
- **Not predicate** is specified by `!` operator (e.g. `!expression` - not
  used in the grammar above).
- **Match actions** are special commands written within `{` and `}` braces
  after a rule (e.g. `some_rule{push, add}`). These commands will be executed
  after the rule has been matched. Each command can have arguments separated
  with the whitespace. If more than one command is specified, the commands
  must be separated by comma `,` delimiter. See below for the list
  of the provided actions.
- **State matches** are given as state names preceded by `@` operator
  (e.g. `@some_state`). A match will succeed only if the current state is
  the same as the provided by the operator state.
- **Push state** is used to push a state onto the stack of the states and
  make it the current. It is specified using `+@` operator with a state name
  after it (e.g. `+@some_state`). Later this state can be matched using
  the `@` operator. This rule always succeeds.
- **Pop state** is used to pop a state form the top of the state stack.
  It is specified using `-@` operator followed by the state name that should
  be removed (e.g. `-@some_state`). If the current state doesn't match
  the specified state then the match fails.
- **Wrapping with a state layer** is specified using `@(` and `)` operator and
  allows one or more rules to be wrapped with a separate state layer
  (e.g. `@( ((LOCAL variable_name{add}) / (variable_name{any} ASSIGN value))* )`).
  It allows to store added by actions data in separate layers (for example,
  to handle local variables).
- A special rule `EOF` will match end of input string.

A set of basic **match actions** if provided:
- **push** to push a matched token onto the stack. This action always succeeds.
- **pop** to match against the token at the top of the stack corresponding
  to the rule and pop that token from the stack. If the matched token and
  the token at the top of the stack aren't the same, then the match will fail.
- **pop_front** to match against the token at the bottom of the stack
  corresponding to the rule and remove that token from the stack.
  If the matched token and the token at the bottom of the stack aren't
  the same, then the match will fail. This action can be used to implement
  FIFO (First In, First Out) rules.
- **add** to add a matched token to the list of the matched tokens
  corresponding to the rule. This action always succeeds and can be used,
  for example, to determine local variables.
- **parent add** to add a matched token to the list of the matched tokens of
  the parent state layer corresponding to the rule. This action always succeeds
  and can be used, for example, to determine local variables.
- **global add** to add a matched token to the list of the matched tokens of
  the global state layer corresponding to the rule. This action always succeeds
  and can be used, for example, to determine global variables.
- **any** to match any token corresponding to the rule that were previously
  added to the list of matched tokens (by **add** action) across all the state
  layers. If no token found, then the rule will fail to match.

In the RHS a rule reference is a name of another rule. Parser will try to match
another rule at that location.

Literal string matches and regex matches follow the same rules as Python itself
would use for
single-quoted
[string literals](https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals),
regarding the escaping of embedded quotes, and the translation of escape
sequences. Literal string matches are treated as normal (non-raw) string
literals, and regex matches are treated as raw string literals. Triple-quoting,
and the 'r', 'u' and 'b' prefixes, are not supported – note than in arpeggio PEG
grammars, all strings are Unicode, and the 'r' prefix denotes a regular
expression.

Creating a parser using PEG syntax is done by the class `ParserPEG` from the
`arpeggio.peg` or `arpeggio.cleanpeg` modules.

```python
from arpeggio.cleanpeg import ParserPEG
parser = ParserPEG(calc_grammar, "calc")
```

Where `calc_grammar` is a string with the grammar given above and the `"calc"`
is the name of the root rule of the grammar.

After this you get the same parser as with the `ParserPython`. There is no
difference at all so you can parse the same language.

```python
input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"
parse_tree = parser.parse(input_expr)
```

!!! note
    Just remember that using textual PEG syntax imposes a slight overhead since
    the grammar must be parsed and the parser for your language must be built by
    semantic analysis of grammar parse tree.  If you plan to instantiate your
    parser once and than use it many times this shall not have that much of
    performance hit but if your workflow introduce instantiating parser each time
    your parse some input than consider defining your grammar using Python as it
    will start faster.  Nevertheless, the parsing performance will be the same in
    both approach since the same code for parsing is used.

