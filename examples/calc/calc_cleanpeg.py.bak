#######################################################################
# Name: calc_peg.py
# Purpose: Simple expression evaluator example using PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2015 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example is functionally equivalent to calc.py. The difference is that
# in this example grammar is specified using PEG language instead of python constructs.
# Semantic actions are used to calculate expression during semantic
# analysis.
# Parser model as well as parse tree exported to dot files should be
# the same as parser model and parse tree generated in calc.py example.
#######################################################################
from __future__ import absolute_import, unicode_literals, print_function

import os
from arpeggio.cleanpeg import ParserPEG
from arpeggio import visit_parse_tree
from calc import CalcVisitor


def main(debug=False):

    # Grammar is defined using textual specification based on PEG language.
    # Load grammar form file.
    calc_grammar = open(os.path.join(os.path.dirname(__file__),
                                     'calc_clean.peg'), 'r').read()

    # First we will make a parser - an instance of the calc parser model.
    # Parser model is given in the form of PEG notation therefore we
    # are using ParserPEG class. Root rule name (parsing expression) is "calc".
    parser = ParserPEG(calc_grammar, "calc", debug=debug)

    # An expression we want to evaluate
    input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"

    # Then parse tree is created out of the input_expr expression.
    parse_tree = parser.parse(input_expr)

    # The result is obtained by semantic evaluation using visitor class.
    # visit_parse_tree will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be evaluated result of the input_expr expression.
    result = visit_parse_tree(parse_tree, CalcVisitor(debug=debug))

    # Check that result is valid
    assert (result - -7.51194444444) < 0.0001

    print("{} = {}".format(input_expr, result))

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

