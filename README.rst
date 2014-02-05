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


INSTALLATION
------------

Arpeggio is written in Python programming language and distributed with setuptools support.
Install it with the following command::

    python setup.py install

after installation you should be able to import arpeggio python module with::

    import arpeggio

There is no documentation at the moment. See examples for some ideas of how it can
be used.


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


