#######################################################################
# Name: simple.py
# Purpose: Simple language based on example from pyPEG
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2015 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example demonstrates grammar definition using python constructs.
# It is taken and adapted from pyPEG project (see http://www.fdik.org/pyPEG/).
#######################################################################


import os

from arpeggio import Kwd, OneOrMore, ParserPython, ZeroOrMore
from arpeggio import RegExMatch as _


# Grammar
def comment():
    return [_(r"//.*"), _(r"(?s)/\*.*?\*/")]


def literal():
    return _(r'\d*\.\d*|\d+|".*?"')


def symbol():
    return _(r"\w+")


def operator():
    return _(r"\+|\-|\*|\/|\=\=")


def operation():
    return symbol, operator, [literal, functioncall]


def expression():
    return [literal, operation, functioncall]


def expressionlist():
    return expression, ZeroOrMore(",", expression)


def returnstatement():
    return Kwd("return"), expression


def ifstatement():
    return Kwd("if"), "(", expression, ")", block, Kwd("else"), block


def statement():
    return [ifstatement, returnstatement], ";"


def block():
    return "{", OneOrMore(statement), "}"


def parameterlist():
    return "(", symbol, ZeroOrMore(",", symbol), ")"


def functioncall():
    return symbol, "(", expressionlist, ")"


def function():
    return Kwd("function"), symbol, parameterlist, block


def simpleLanguage():
    return function


def main(debug=False):
    # Load test program from file
    current_dir = os.path.dirname(__file__)
    with open(os.path.join(current_dir, "program.simple")) as f:
        test_program = f.read()

    # Parser instantiation. simpleLanguage is the definition of the root rule
    # and comment is a grammar rule for comments.
    parser = ParserPython(simpleLanguage, comment, debug=debug)

    parser.parse(test_program)


if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)
