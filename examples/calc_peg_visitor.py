#######################################################################
# Name: calc_peg.py
# Purpose: Simple expression evaluator example using PEG language and
#   visitor pattern for semantic analysis.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example is functionally equivalent to calc_peg.py.
# It is a demonstration of visitor pattern approach for semantic analysis.
# Parser model as well as parse tree exported to dot files should be
# the same as parser model and parse tree generated in calc.py example.
#######################################################################
from __future__ import absolute_import, unicode_literals, print_function
try:
    text = unicode
except:
    text = str

from arpeggio.cleanpeg import ParserPEG
from arpeggio import PTNodeVisitor, visit_parse_tree


# Grammar is defined using textual specification based on PEG language.
calc_grammar = """
        number = r'\d*\.\d*|\d+'
        factor = ("+" / "-")?
                  (number / "(" expression ")")
        term = factor (( "*" / "/") factor)*
        expression = term (("+" / "-") term)*
        calc = expression+ EOF
"""


class CalcVisitor(PTNodeVisitor):

    def visit_number(self, node, children):
        """
        Converts node value to float.
        """
        if self.debug:
            print("Converting {}.".format(node.value))
        return float(node.value)

    def visit_factor(self, node, children):
        """
        Removes parenthesis if exists and returns what was contained inside.
        """
        if self.debug:
            print("Factor {}".format(children))
        if len(children) == 1:
            return children[0]
        sign = -1 if children[0] == '-' else 1
        return sign * children[-1]

    def visit_term(self, node, children):
        """
        Divides or multiplies factors.
        Factor nodes will be already evaluated.
        """
        if self.debug:
            print("Term {}".format(children))
        term = children[0]
        for i in range(2, len(children), 2):
            if children[i-1] == "*":
                term *= children[i]
            else:
                term /= children[i]
        if self.debug:
            print("Term = {}".format(term))
        return term

    def visit_expression(self, node, children):
        """
        Adds or substracts terms.
        Term nodes will be already evaluated.
        """
        if self.debug:
            print("Expression {}".format(children))
        expr = 0
        start = 0
        # Check for unary + or - operator
        if text(children[0]) in "+-":
            start = 1

        for i in range(start, len(children), 2):
            if i and children[i - 1] == "-":
                expr -= children[i]
            else:
                expr += children[i]

        if self.debug:
            print("Expression = {}".format(expr))

        return expr


def main(debug=False):

    # First we will make a parser - an instance of the calc parser model.
    # Parser model is given in the form of PEG notation therefore we
    # are using ParserPEG class. Root rule name (parsing expression) is "calc".
    parser = ParserPEG(calc_grammar, "calc", debug=debug)

    # An expression we want to evaluate
    input_expr = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"

    # Then parse tree is created out of the input_expr expression.
    parse_tree = parser.parse(input_expr)

    result = visit_parse_tree(parse_tree, CalcVisitor(debug=debug))

    # visit_parse_tree will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be evaluated result of the input_expr expression.
    print("{} = {}".format(input_expr, result))

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=False)

