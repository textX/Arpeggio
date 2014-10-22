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
unambiguous. This is achieved by making choice operator ordered. In PEGs a first choice from
left to right that matches will be used.

PEG grammar is a set of PEG rules. PEG rules consists of parsing expressions and can reference (call)
each other.

Example grammar in PEG notation:

.. code::

  first = 'first' second+ EOF
  second = 'a' / 'b'

In this example ``first`` is the root rule. This rule will match a literal string ``first`` followed
by one or more ``second`` rule (this is a rule reference) followed by end of input (``EOF``).
``second`` rule is ordered choice and will match either ``a`` or ``b`` in that order.

During parsing each successfully matched rule will create a parse tree node (see `Parse tree`_).

In Arpeggio each PEG rule consists of atomic parsing expression which can be:

- **terminal match rules** - create a `Terminal nodes`_:

  - **String match** - a simple string that is matched literally from the input string.
  - **RegEx match** - regular expression match (based on python ``re`` module).

- **non-terminal match rules** - create a `Non-terminal nodes`_:

  - **Sequence** - succeeds if all parsing expressions matches at current location in the defined order.
    Matched input is consumed.
  - **Ordered choice** - succeeds if any of the given expressions matches at the current location. The
    match is tried in the order defined. Matched input is consumed.
  - **Zero or more** - given expression is matched until match is successful. Always succeeds. Matched input
    is consumed.
  - **One or more** - given expressions is matched until match is successful. Succeeds if at least one
    match is done. Matched input is consumed.
  - **Optional** - matches given expression but will not fail if match can't be done. Matched input is
    consumed.
  - **And predicate** - succeeds if given expression matches at current location but does not
    consume any input.
  - **Not predicate** - succeeds if given expression **does not** matches at current location but
    does not consume any input.

PEG grammars in Arpeggio may be written twofold:

- Using Python statements and expressions.
- Using textual PEG syntax (currently there are two variants, see below).


Grammars written in Python
--------------------------

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
of ``number`` rule and a sequence of ``expression`` rule in brackets.
This rule will match an optional sign (``+`` or ``-`` checked in that order) after which follows a ``number``
or an ``expression`` in brackets (checked in that order).

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

You can navigate and analyze parse tree or transform it using visitor pattern to some more
usable form (see `Semantic analysis - Visitors`_)

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

.. image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/docs/images/calc_parser_model.dot.png
   :height: 600


Grammars written in PEG notations
---------------------------------

Grammars can also be specified using PEG notation. There are actually two of them at the moment and
both notations are implemented using canonical Python based grammars (see modules ``arpeggio.peg`` and
``arpeggio.cleanpeg``).

There are no significant differences between those two syntax. The first one use more traditional approach
using ``<-`` for rule assignment, ``//`` for line comments and ``;`` for the rule terminator.
The second syntax (from ``arpeggio.cleanpeg``) uses ``=`` for assignment, does not use rule terminator
and use ``#`` for line comments. Which one you choose is totally up to you. If your don't like any
of these syntaxes you can make your own (look at ``arpeggio.peg`` and ``arpeggio.cleanpeg`` modules
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

Here is an example parse tree for the ``calc`` grammar and the expression "-(4-1)*5+(2+4.67)+5.89/(.2+7)":

.. image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/docs/images/calc_parse_tree.dot.png
   :height: 500

Each non-leaf node is non-terminal. The name in in this nodes are the names of the grammar PEG rules that
created them.

The leaf nodes are terminals and they are matched by the string match or regex match rules.

In the square brackets is the location in the input stream where the terminal/non-terminal is recognized.

Terminal nodes
~~~~~~~~~~~~~~
Terminals in Arpeggio are created by the specializations of the ``Match`` class:

- ``StrMatch`` if the literal string is matched from the input or
- ``RegExMatch`` if a regular expression is used to match input.

Non-terminal nodes
~~~~~~~~~~~~~~~~~~
Non-terminal nodes are non-leaf nodes of the parse tree. They are created by PEG grammar rules.
Children of non-terminals can be other non-terminals or terminals.

For example, nodes with the labels ``expression``, ``factor`` and ``term`` from the above parse
tree are non-terminal nodes created by the rules with the same names.

Parse tree navigation
~~~~~~~~~~~~~~~~~~~~~
Usually we want to transform parse tree to some more usable form or to extract some data from it.
Parse tree can be navigated using following approaches:

TODO


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

By default, if NoMatch is not caught you will get detailed explanation of the error on the console.
The exact location will be reported, the context (part of the input where the error occurred) and the first
rule that was tried at that location.

Example:

.. code:: python

    parser = ParserPython(calc)
    # 'r' in the following expression can't be recognized by
    # calc grammar
    input_expr = "23+4/r-89"
    parse_tree = parser.parse(input_expr)

.. code::

  Traceback (most recent call last):
    ...
  arpeggio.NoMatch: Expected '+' at position (1, 6) => '23+4/*r-89'.

The place in the input stream is marked by ``*`` and the position in row, col is given ``(1, 6)``.

If you wish more control on error reporting (e.g. you are using Arpeggio in GUI application and want to
report error to the user) you can catch ``NoMatch`` in your code and inspect its attributes.

.. code:: python

    try:
      parser = ParserPython(calc)
      input_expr = "23+4/r-89"
      parse_tree = parser.parse(input_expr)
    except NoMatch as e:
      # Do something with e


``NoMatch`` class has following attributes:

- rule: A ``ParsingExpression`` rule that is the source of the exception.
- position: A position in the input stream where exception occurred.
- parser (Parser): A ``Parser`` instance.
- exp_str: What is expected? If not given it is deduced from the rule.
  Used for nicer error reporting.

The ``position`` is given as the offset from the beginning of the input string. To convert it to row and column
use ``pos_to_linecol`` method on the parser.

.. code:: python

    try:
      parser = ParserPython(calc)
      input_expr = "23+4/r-89"
      parse_tree = parser.parse(input_expr)
    except NoMatch as e:
      line, col = e.parser.pos_to_linecol(e.position)
      ...

Currently Arpeggio will report the first rule it tried at that location.
Arpeggio is backtracking parser, which means that it will go back and try another alternatives when the match
does not succeeds but it will nevertheless report the furthest place in the input where it failed.

Parser configuration
--------------------

Case insensitive parsing
~~~~~~~~~~~~~~~~~~~~~~~~
By default Arpeggio is case sensitive. If you wish to do case insensitive parsing set parser parameter
``ignore_case`` to ``True``.

.. code:: python

  parser = ParserPython(calc, ignore_case=True)


White-space handling
~~~~~~~~~~~~~~~~~~~~
Arpeggio by default skips whitespaces. You can change this behaviour with the parameter ``skipws`` given to
parser constructor.

.. code:: python

  parser = ParserPython(calc, skipws=False)

You can also change what is considered a whitespace by Arpeggio using the ``ws`` parameter. It is a plain string
that consists of white-space characters. By default it is set to "\t\n\r ".

For example, to prevent a newline to be treated as whitespace you could write:

.. code:: python

  parser = ParserPython(calc, ws='\t\r ')


Comment handling
~~~~~~~~~~~~~~~~
Support for comments in your language can be specified as another set of grammar rules.
See ``simple.py`` example.

Parser is constructed using two parameters.

.. code:: python

  parser = ParserPython(simpleLanguage, comment)

First parameter is the root rule while the second is a rule for comments.

During parsing comment parse trees are kept in the separate list thus comments will not show in the main parse
tree.

.. warning::

  Be aware that `semantic analysis <#Semantic analysis - Visitors>`_ operates on nodes of finished parse tree
  and therefore on reduced tree some ``visit_xxx`` actions will not get called.


Parse tree reduction
~~~~~~~~~~~~~~~~~~~~
Non-terminals are by default created for each rule. Sometimes it can result in trees of great depth.
You can alter this behaviour setting ``reduce_tree`` parameter to ``True``.

.. code:: python

  parser = ParserPython(calc, reduce_tree=True)

In this configuration non-terminals with single child will be removed from the parse tree.

For example, ``calc`` parse tree above will look like this:

.. image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/docs/images/calc_parse_tree_reduced.dot.png
   :height: 400

Notice the removal of each non-terminal with single child.

Semantic analysis - Visitors
----------------------------

You will surely always want to extract some information from the parse tree or to transform it in some
more usable form.
The process of parse tree transformation to other forms is referred to as *semantic analysis*.
You could do that using parse tree navigation etc. but it is better to use some
standard mechanism.

In Arpeggio a visitor pattern is used for semantic analysis. You write a python class that inherits
``PTNodeVisitor`` and has a methods of the form ``visit_<rule name>(self, node, children)`` where
rule name is a rule name from the grammar.

.. code:: python

  class CalcVisitor(PTNodeVisitor):

      def visit_number(self, node, children):
          return float(node.value)

      def visit_factor(self, node, children):
          if len(children) == 1:
              return children[0]
          sign = -1 if children[0] == '-' else 1
          return sign * children[-1]

      ...


During a semantic analysis a parse tree is walked in the depth-first manner and for each node a proper visitor
method is called to transform it to some other form. The results are than fed to the parent node visitor method.
This is repeated until the final, top level parse tree node is processed (its visitor is called).
The result of the top level node is the final output of the semantic analysis.


To apply your visitor class on the parse tree use ``visit_parse_tree`` function.

.. code:: python

  result = visit_parse_tree(parse_tree, CalcVisitor(debug=True))

The first parameter is a parse tree you get from the ``parser.parse`` call while the second parameter is an
instance of your visitor class. Semantic analysis can be run in debug mode if you set ``debug`` parameter
to ``True`` during visitor construction. You can use this flag to print your own debug information from 
visitor methods.

.. code:: python

  class MyLanguageVisitor(PTNodeVisitor):

    def visit_somerule(self, node, children):
      if self.debug:
        print("Visiting some rule!")

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
This class is a list-like structure that holds the results of semantic evaluation from the children parse
tree nodes (analysis is done bottom-up).

To suppress node completely return ``None`` from visitor method. In this case the parent visitor method will
not get this node in its ``children`` parameter.

In the `calc.py <https://github.com/igordejanovic/Arpeggio/blob/master/examples/calc.py>`_ example a
semantic analysis (``CalcVisitor`` class) will evaluate the expression. The parse tree is thus transformed
to a single numeric value that represent the result of the expression.

In the `robot.py <https://github.com/igordejanovic/Arpeggio/blob/master/examples/calc.py>`_ example a
semantic analysis (``RobotVisitor`` class) will evaluate robot program (transform its parse tree) to the
final robot location.

Semantic analysis can do a complex stuff. For example,
see `peg_peg.py <https://github.com/igordejanovic/Arpeggio/blob/master/examples/peg_peg.py>`_ example and 
`PEGVisitor <https://github.com/igordejanovic/Arpeggio/blob/master/arpeggio/peg.py>`_ class where the
PEG parser for the given language is built using semantic analysis.


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

This behaviour can be disabled setting parameter ``defaults`` to ``False`` on visitor construction.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

