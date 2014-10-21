.. Arpeggio documentation master file, created by
   sphinx-quickstart on Sat Oct 11 16:31:23 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Arpeggio's documentation!
====================================

Arpeggio is recursive descent parser with backtracking and memoization (a.k.a. pacrat parser).
Arpeggio grammars are based on `PEG formalism <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`_.


PEG grammars
------------

PEG is a type of formal grammar that is given as a set of rules for recognizing strings of the language.
In a way it is similar to context-free grammars with a very important distinction that PEG are always
unambiguous. This is achieved by making choice opearator ordered. In PEGs a first choice from
left to right that matches will be used.

In Arpeggio each PEG rule consists of atomic parsing expression which can be:

  - **terminal match rules**:

    - **String match** - a simple string that is matched literaly from the input string.
    - **RegEx match** - regular expression match (based on python ``re`` module).

  - **non-terminal match rules**:

    - **Sequence**

TODO: Finis this section.



Grammar given in Python
-----------------------

Canonical form of grammar specification uses Python statements and expressions.

Here is an example of arpeggio grammar for simple calculator:

.. code:: python

  def number():     return _(r'\d*\.\d*|\d+')
  def factor():     return Optional(["+","-"]), [number,
                            ("(", expression, ")")]
  def term():       return factor, ZeroOrMore(["*","/"], factor)
  def expression(): return term, ZeroOrMore(["+", "-"], term)
  def calc():       return OneOrMore(expression), EOF


Each rule is given in the form of Python function. Python function returns data structure
that maps to PEG expressions.

- **Sequence** is represented as Python tuple.
- **Ordered choice** is represented as Python list where each element is one alternative.
- **One or more** is represented as an instance of ``OneOrMore`` class.
  The parameters are treated as a containing sequence.
- **Zero or more** is represented as an instance of ``ZeroOrMore`` class.
  The parameters are treated as a containing sequence.
- **Optional** is represented as an instance of ``Optional`` class.
- **And predicate** is represented as an instance of ``And`` class.
- **Not predicate** is represented as an instance of ``Not`` class.
- **Literal string match** is represented as string or regular expression given as an instance of
  ``RegExMatch`` class.
- **End of string/file** is recoginzed by the ``EOF`` special rule.

For example, the ``calc`` language consists of one or more ``expression`` and end of file.

``factor`` rule consists of optional ``+`` or ``-`` char
matched in that order (they are given in Python list thus ordered choice) followed by the ordered choice
of ``number`` rule and sequence of ``expression`` rule in brackets.

From this description Arpeggio builds **the parser model**. Parser model is a graph of recursive parser expressions.
This is done during parser instantiation. For example, to instantiate ``calc`` parser you do the following:

.. code:: python

    parser = ParserPython(calc)

Where ``calc`` is the function defining the root rule of your grammar.
There is no code generation. Parser works as an interpreter for your grammar.
The grammar is used to configure Arpeggio parser to recognize your language
(in this case the ``calc`` language).

After parser construction your can call ``parser.parse`` to parse your input text.

.. code:: python

    input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"
    parse_tree = parser.parse(input_expr)

You can navigate and analyze parse tree or transform it using visitor patter to some more
usable form.

If you want to debug parser construction set ``debug`` parameter to ``True`` in the ``ParserPython`` call.

.. code:: python

    parser = ParserPython(calc, debug=True)

In this case a verbose messages will be printed during parser construction and the 
``dot`` file (from `graphviz software package <http://www.graphviz.org/content/dot-language>`_)
will be created if the parser model is constructed without errors. This dot file can be 
rendered as image using one of available dot viewer software or transformed to an image using ``dot`` tool.

.. code:: bash

  $ dot -Tpng -O calc_parser_model.dot

After this command you will get ``calc_parser_model.dot.png`` file which can be opened in any ``png`` image
viewer. This image shows the graph representing the parser model which looks like this:

|calc_parser_model|


PEG notations
-------------

Grammars can also be specified using PEG notation. There are actually two of them at the moment and
both notations are implemented using canonical Python based grammars (see modules ``arpeggio.peg`` and
``arpeggio.cleanpeg``).

There are no significant differences between those two syntax. The first one use more traditional approach
using ``<-`` for rule assignment, ``//`` for line comments and ``;`` for the rule terminator.
The second syntax (from ``arpeggio.cleanpeg``) uses ``=`` for assignment, does not use rule terminator
and use ``#`` for line comments. Which one your choose is totally up to you. If your don't like any
of these syntaxes you can make your own (just start with ``arpeggio.peg`` and ``arpeggio.cleanpeg`` modules
as an examples).

An example of the ``calc`` grammar given in PEG syntax (``arpeggio.cleanpeg``):

.. code::

    number = r'\d*\.\d*|\d+'
    factor = ("+" / "-")?
              (number / "(" expression ")")
    term = factor (( "*" / "/") factor)*
    expression = term (("+" / "-") term)*
    calc = expression+ EOF

Creating a parser using PEG syntax is done by the class ``ParserPEG`` from the ``arpeggio.peg`` or
``arpeggio.cleanpeg`` modules.

.. code:: python

    from arpeggio.cleanpeg import ParserPEG
    parser = ParserPEG(calc_grammar, "calc")

Where ``calc_grammar`` is a string with the grammar given above and the ``"calc"`` is the name of the root
rule of the grammar.

After this you get the same parser as with the ``ParserPython``. There is no difference at all so you
can parse the same language.

.. code:: python

    input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"
    parse_tree = parser.parse(input_expr)


.. warning::
  Just remember that using textual PEG syntax imposes a slight overhead since the grammar must be parsed and
  the parser for your language must be built by semantic analysis of grammar parse tree.
  If you plan to instantiate your parser once and than use it many times this will not have that much of
  performance hit but if your workflow introduce instantiating parser each time your parse some input than
  consider defining your grammar using Python as it will start faster.
  Nevertheless, the parsing performance will be the same in both approach since the same code for parsing
  is used.

Parse tree
----------

Parse tree or concrete syntax tree is a tree structure built from the input string during parsing.
It represent the structure of the input string. Each node in the parse tree is either a ``terminal``
or ``non-terminal``. Terminals are the leafs of the tree while the inner nodes are non-terminals.

Here is an example parse tree for the ``calc`` grammar:


Terminals
~~~~~~~~~
Terminals in Arpeggio are created by the specializations of the ``Match`` class: ``StrMatch`` if
the literal string is matched from the input or ``RegExMatch`` if a regular expression is used to
match input.

NonTerminals
~~~~~~~~~~~~
Non-terminal nodes are non-leaf nodes of the parse tree. Children of non-terminals can be other non-terminals
or terminals.

For example, nodes .... from the above parse tree are non-terminal nodes.

Parse tree navigation
~~~~~~~~~~~~~~~~~~~~~
Usually we want to transform parse tree to some more usable form or to extract some data from it.
Parse tree can be navigated using following approaches:

Grammar debugging
-----------------
During grammar design you can make syntax and semantic errors. Arpeggio will report any syntax error
with all the necessary informations whether you are building parser from python expressions or from
a textual PEG notation.

For semantic error you have a debugging mode of operation which is entered by setting ``debug`` param
to ``True`` in the parser construction call. When Arpeggio runs in debug mode it will print a detailed
information of what it is doing. Furthermore a ``dot`` files will be generated that visually represents
your grammar (this is known in Arpeggio as ``the parser model``). In debug mode also a parse tree will
also be rendered to ``dot`` file when you parse your input with properly constructed parser.

You can visualize ``dot`` files using some of available dot viewer or you can convert dot file to image
using ``dot`` tool from ``graphviz`` package.

An example to convert ``calc_parser_model.dot`` to ``png`` file use:

.. code:: bash

  $ dot -Tpng -O calc_parser_model.dot

Errors in the input
-------------------
If your grammar is correct but you get input string with syntax error parser will raise ``NoMatch`` exception
with the information where in the input stream error has occurred and what the parser expect to see at that
location.

The input location is given as the offset from the beginning of the input string. To convert it to row and column
use ``position_to_row_col`` method on the parser.

Example:

.. code:: python


Currently Arpeggio will report the first rule it tried at that location.
Arpeggio is backtracking parser, which means that it will go back and try another alternatives when the match
does not succeeds but it will nevertheless report the furthest place in the input where it failed.


Semantic analysis - Visitors
----------------------------

You will surely always want to extract some information from the parse tree or to transform it in some
more usable form.
The process of parse tree transformation to other forms is referred to as *semantic analysis*.
You could do that using plain tree navigation etc. but it is better to use some
standard mechanism.

In Arpeggio a visitor pattern is used for semantic analysis. You write a python class that has a methods named
``visit_<rule name>`` where rule name is a rule name from the grammar.
During a semantic analysis a parse tree is walked in the depth-first manner and for each node a proper visitor
method is called to transform it to some other form. The results are than fed to the parent node visitor method.
This is repeated until the final, top level parse tree node is processed (its visitor is called).
The result of the top level node is the final output of the semantic analysis.


To apply your visitor class on the parse tree use ``visit_parse_tree`` function.

Example:

.. code:: python

  result = visit_parse_tree(parse_tree, CalcVisitor(debug=True))

The first parameter is a parse tree you get from the ``parser.parse`` call while the second parameter is an
instance of the your visitor class. Semantic analysis can be run in debug mode if you set ``debug`` parameter
to ``True`` during visitor construction.

During semantic analysis, each ``visitor_xxx`` method gets current parse tree node as the first parameter and
the evaluated children nodes as the second parameter.

For example, if you have ``expression`` rule in your grammar than the transformation of the non-terminal
matched by this rule can be done as:

.. code:: python
  def visitor_expression(self, node, children):
    ...
    return transformed node


``node`` is the current ``NonTerminal`` or ``Terminal`` from the parse tree while the ``children`` is
instance of ``SemanticResults`` class.
This class is a list like structure that holds the results of semantic evaluation from the children parse
tree nodes (analysis is done bottom-up).

In the ``calc.py`` example a semantic analysis will evaluate the expression. The parse tree is thus transformed
to a single numeric value that represent the result of the expression.

In the ``robot.py`` example a semantic analysis will evaluate robot program (transform its parse tree) to the
final robot location.

Semantic analysis can do a complex stuff. For example, see ``peg_peg.py`` example where the PEG parser for
the given language is built using semantic analysis.


SemanticResults
~~~~~~~~~~~~~~~
Class of object returned from the parse tree nodes evaluation. Used for filtering and navigation over evaluation
results on children nodes.

TODO: Describe class in more details.

Default actions
~~~~~~~~~~~~~~~
For each parse tree node that does not have an appropriate ``visitor_xxx`` call a default action is performed.
If the node is created by a plain string match action will return ``None`` and thus suppress this node.
This is handy for all those syntax noise (bracket, braces, keywords etc.).

For example, if your grammar is:

.. code::

  number_in_brackets = "(" number ")"
  number = r'\d+'

Than the default action for ``number`` will return number converted to string and the default action for
``(`` and ``)`` will return ``None`` and thus suppress this nodes so the visitor method for ``number_in_brackets``
rule will only see ``number`` child.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

