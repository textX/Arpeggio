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

Terminals
~~~~~~~~~

NonTerminals
~~~~~~~~~~~~

Parse tree navigation
~~~~~~~~~~~~~~~~~~~~~

Errors in grammar
-----------------

Errors in input
---------------

Semantic analysis - Visitors
----------------------------


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

