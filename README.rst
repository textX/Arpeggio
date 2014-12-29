.. image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/art/arpeggio-logo.png
   :height: 100

Arpeggio - PEG parser
=====================

|build-status| |docs|

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

Quick start
-----------

Write a grammar. There are several ways to do that:

- The canonical grammar format uses Python statements and expressions.
  Each rule is specified as Python function which should return a data
  structure that defines the rule. For example a grammar for simple 
  calculator can be written as:

  .. code:: python

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

- The same grammar could also be written using traditional textual PEG syntax like this:

  ::

    number <- r'\d*\.\d*|\d+';  // this is a comment
    factor <- ("+" / "-")?
              (number / "(" expression ")");
    term <- factor (( "*" / "/") factor)*;
    expression <- term (("+" / "-") term)*;
    calc <- expression+ EOF;

- Or similar syntax but a little bit more readable like this:

  ::

    number = r'\d*\.\d*|\d+'    # this is a comment
    factor = ("+" / "-")?
              (number / "(" expression ")")
    term = factor (( "*" / "/") factor)*
    expression = term (("+" / "-") term)*
    calc = expression+ EOF

  The second and third options are implemented using canonical first form.
  Feel free to implement your own grammar syntax if you don't like these
  (see modules ``arpeggio.peg`` and ``arpeggio.cleanpeg``).

Instantiate a parser. Parser works as grammar interpreter. There is no code generation.

.. code:: python

    from arpeggio import ParserPython
    parser = ParserPython(calc)   # calc is the root rule of your grammar
                                  # Use param debug=True for verbose debugging
                                  # messages and grammar and parse tree visualization
                                  # using graphviz and dot

Parse your inputs.

.. code:: python

    parse_tree = parser.parse("-(4-1)*5+(2+4.67)+5.89/(.2+7)")

Analyze parse tree directly or write a visitor class to transform it to a more
usable form. See examples how it is done.

For textual PEG syntaxes instead of ``ParserPyton`` instantiate ``ParserPEG``
from ``arpeggio.peg`` or ``arpeggio.cleanpeg`` modules. See examples how it is done.

To debug your grammar set ``debug`` parameter to ``True``. A verbose debug
messages will be printed and a dot files will be generated for parser model (grammar)
and parse tree visualization.

Here is an image rendered using graphviz of parser model for 'calc' grammar.

.. image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/docs/images/calc_parser_model.dot.png
  :scale: 50%

And here is an image rendered for parse tree for the above parsed calc expression.

.. image:: https://raw.githubusercontent.com/igordejanovic/Arpeggio/master/docs/images/calc_parse_tree.dot.png

If you are building a domain-specific language then I suggest you to take a look at `textX`_.

Learn more
----------

Arpeggio documentation is available `here <http://arpeggio.readthedocs.org/en/latest/>`_.

Also, check out `examples <https://github.com/igordejanovic/Arpeggio/tree/master/examples>`_.

Discuss, ask questions
----------------------
Please use `discussion forum`_ for general discussions, suggestions etc.

If you are on stackoverflow_ you can ask questions there.
Just make sure to tag your question with ``arpeggio`` so that your question
reach me.

Contribute
----------
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


.. _textX: https://github.com/igordejanovic/textX
.. _discussion forum: https://groups.google.com/forum/?hl=en#!forum/arpeggio-talk
.. _stackoverflow: http://stackoverflow.com/
.. _project on github: https://github.com/igordejanovic/Arpeggio/
.. _PEP-8 guidelines: http://legacy.python.org/dev/peps/pep-0008/
.. _issue tracker: https://github.com/igordejanovic/Arpeggio/issues/

Why is it called arpeggio?
--------------------------

In music, arpeggio is playing the chord notes one by one in sequence. I came up with the name by thinking that parsing is very similar to arpeggios in music. You take tokens one by one from an input and make sense out of it – make a chord!

Well, if you don't buy this maybe it is time to tell you the truth. I searched the dictionary for the words that contain PEG acronym and the word arpeggio was at the top of the list ;)


.. |build-status| image:: https://readthedocs.org/projects/arpeggio/badge/?version=latest
   :target: https://readthedocs.org/projects/arpeggio/?badge=latest
   :alt: Documentation Status

.. |docs| image:: https://travis-ci.org/igordejanovic/Arpeggio.svg
   :target: https://travis-ci.org/igordejanovic/Arpeggio

