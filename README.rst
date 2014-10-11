Arpeggio - Packrat parser interpreter
=====================================

Arpeggio is PEG grammar interpreter implemented as recursive descent
parser with memoization (aka Packrat parser).

Arpeggio is a part of the research project whose main goal is building environment for DSL development.
The main domain of application is IDE for DSL development but it can be used for all
sort of general purpose parsing.

For more information on PEG and packrat parsers see:
 * http://pdos.csail.mit.edu/~baford/packrat/
 * http://pdos.csail.mit.edu/~baford/packrat/thesis/
 * http://en.wikipedia.org/wiki/Parsing_expression_grammar


Installation
------------

Arpeggio is written in Python programming language and distributed with setuptools support.
Install it with from pypi with the following command::

    pip install Arpeggio

Or from source with::

    python setup.py install

after installation you should be able to import arpeggio python module with::

    import arpeggio

There is no documentation at the moment. See examples for some ideas of how it can
be used.

Quick start
-----------

1. Write a grammar. There are several ways to do that:

a) The canonical grammar format uses Python statements and expressions. Each rule is specified as Python function which should return a data structure that defines the rule. For example a grammar for simple calculator can be written as::

  from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF
  from arpeggio import RegExMatch as _

  def number():     return _(r'\d*\.\d*|\d+')
  def factor():     return Optional(["+","-"]),
                          [number, ("(", expression, ")")]
  def term():       return factor, ZeroOrMore(["*","/"], factor)
  def expression(): return term, ZeroOrMore(["+", "-"], term)
  def calc():       return OneOrMore(expression), EOF

  The python lists in the data structure represent ordered choices while the tuples represent sequences from the PEG.
  For terminal matches use plain strings or regular expressions.

b) The same grammar could also be written using traditional textual PEG syntax like this::

  number <- r'\d*\.\d*|\d+';  // this is a comment
  factor <- ("+" / "-")?
            (number / "(" expression ")");
  term <- factor (( "*" / "/") factor)*;
  expression <- term (("+" / "-") term)*;
  calc <- expression+ EOF;

c) Or similar syntax but a little bit more readable like this::

  number = r'\d*\.\d*|\d+'    # this is a comment
  factor = ("+" / "-")?
            (number / "(" expression ")")
  term = factor (( "*" / "/") factor)*
  expression = term (("+" / "-") term)*
  calc = expression+ EOF

The second and third options are implemented using canonical first form. Feel free to implement your own grammar syntax if you don't like these (see modules :code:`arpeggio.peg` and :code:`arpeggio.cleanpeg`).

2. Instantiate a parser. Parser works as grammar interpreter. There is no code generation::

    from arpeggio import ParserPython
    parser = ParserPython(calc)   # calc is the root rule of your grammar
                                  # Use param debug=True for verbose debugging messages and
                                  # grammar and parse tree visualization using graphviz and dot

3. Parse your inputs::

    parse_tree = parser.parse("-(4-1)*5+(2+4.67)+5.89/(.2+7)")

4. Analyze parse tree directly or write semantic actions to transform it to a more usable form. See examples how it is done.

5. For textual PEG syntaxes instead of :code:`ParserPyton` instantiate :code:`ParserPEG` from :code:`arpeggio.peg` or :code:`arpeggio.cleanpeg` modules. See examples how it is done.

To debug your grammar set :code:`debug` parameter to :code:`True`. A verbose debug messages will be printed and a dot files will be generated for parser model (grammar) and parse tree visualization.

Here is an image rendered using graphviz of parser model for 'calc' grammar.

|calc_parser_model.dot|

And here is an image rendered for parse tree for the above parsed calc expression.

|calc_parse_tree.dot|

.. |calc_parser_model.dot| image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/docs/images/calc_parser_model.dot.png
  :scale: 50 %
.. |calc_parse_tree.dot| image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/docs/images/calc_parse_tree.dot.png

OVERVIEW
--------

Here is a basic explanation of how arpeggio works and the definition of some terms
used in the arpeggio project.

Language grammar is specified using PEG's textual notation (similar to EBNF) or
python language constructs (lists, tuples, functions...). Parser is directly modeled
by the given grammar so this grammar representation,
whether in textual or python form, is referred to as "the parser model".

Parser is constructed out of the parser model.
Parser is a graph of python objects where each object is an instance of a class
which represents parsing expressions from PEG (e.g. Sequence, OrderedChoice, ZeroOrMore).
This graph is referred to as "the parser model instance" or just "the parser model".

Arpeggio works in interpreter mode. There is no parser code generation.
Given the language grammar Arpeggio will create parser on the fly.
Once constructed, the parser can be used to parse different input strings.
We can think of Arpeggio as the PEG grammar interpreter.
It reads PEG "programs" and executes them.

This design choice requires some upfront work during an initialization phase so Arpeggio
may not be well suited for one-shot parsing where the parser needs to be initialized
every time parsing is performed and the speed is of the utmost importance.
Arpeggio is designed to be used in integrated development environments where the parser
is constructed once (usually during IDE start-up) and used many times.

Once constructed, parser can be used to transform input text to a tree 
representation where the tree structure must adhere to the parser model (grammar).
This tree representation is called "the parse tree".
After construction of the parse tree it is possible to construct Astract Syntax Tree (AST) or,
more generally, Abstract Semantic Graph(ASG) using semantic actions.
ASG is constructed using two-pass bottom-up walking of the parse tree.
ASG, generally has a graph structure, but it can be any specialization of it 
(a tree or just a single node - see calc.py for the example of ASG constructed as 
a single node/value).

Semantic actions are executed after parsing is complete so that multiple different semantic
analysis can be performed on the same parse tree.

Python module arpeggio.peg is a good demonstration of how semantic action can be used
to build PEG parser itself. See also peg_peg.py example where PEG parser is bootstraped
using description given in PEG language itself.


Questions, discussion etc.
--------------------------
Please use `discussion forum`_ for general discussions, suggestions etc.

If you have some specific question on textX usage please use `stackoverflow`_.
Just make sure to tag your question with :code:`arpeggio`.

Contributions
-------------
Arpeggio is open for contributions. You can contribute code, documentation, tests, bug reports.
If you plan to make a contribution it would be great if you first announce that on the discussion forum.

For bug reports please use github `issue tracker`_.

For code/doc/test contributions do the following:

#. Fork the `project on github`_.
#. Clone your fork.
#. Make a branch for the new feature and switch to it.
#. Make one or more commits.
#. Push your branch to github.
#. Make a pull request. I will look at the changes and if everything is ok I will pull it in.

Note: For code contributions please try to adhere to the `PEP-8 guidelines`_. Although I am not strict in that regard it is useful to have a common ground for coding style. To make things easier use tools for code checking (PyLint, PyFlakes, pep8 etc.).


.. _discussion forum: https://groups.google.com/forum/?hl=en#!forum/arpeggio-talk
.. _stackoverflow: http://stackoverflow.com/
.. _project on github: https://github.com/igordejanovic/Arpeggio/
.. _PEP-8 guidelines: http://legacy.python.org/dev/peps/pep-0008/
.. _issue tracker: https://github.com/igordejanovic/Arpeggio/issues/

Why is it called arpeggio?
--------------------------

In music, arpeggio is playing the chord notes one by one in sequence. I came up with the name by thinking that parsing is very similar to arpeggios in music. You take tokens one by one from an input and make sense out of it – make a chord!

Well, if you don't buy this maybe it is time to tell you the truth. I searched the dictionary for the words that contain PEG acronym and the word arpeggio was at the top of the list ;)
