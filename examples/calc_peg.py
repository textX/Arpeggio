#######################################################################
# Name: calc_peg.py
# Purpose: Simple expression evaluator example using PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
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

from arpeggio.cleanpeg import ParserPEG

# Semantic actions
from calc import to_floatSA, factorSA, termSA, exprSA

# Grammar is defined using textual specification based on PEG language.
calc_grammar = """
        number = r'\d*\.\d*|\d+'
        factor = ("+" / "-")?
                  (number / "(" expression ")")
        term = factor (( "*" / "/") factor)*
        expression = term (("+" / "-") term)*
        calc = expression+ EOF
"""

# Rules are mapped to semantic actions
sem_actions = {
    "number" : to_floatSA,
    "factor" : factorSA,
    "term"   : termSA,
    "expression" : exprSA,
}

def main(debug=False):

    # First we will make a parser - an instance of the calc parser model.
    # Parser model is given in the form of PEG notation therefore we
    # are using ParserPEG class. Root rule name (parsing expression) is "calc".
    parser = ParserPEG(calc_grammar, "calc", debug=debug)

    # An expression we want to evaluate
    input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"

    # Then parse tree is created out of the input_expr expression.
    parse_tree = parser.parse(input_expr)

    result = parser.getASG(sem_actions)

    # getASG will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be evaluated result of the input_expr expression.
    # Semantic actions are supplied to the getASG function.
    print("{} = {}".format(input_expr, result))

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=False)

