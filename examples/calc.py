#######################################################################
# Name: calc.py
# Purpose: Simple expression evaluator example
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example demonstrates grammar definition using python constructs as
# well as using semantic actions to evaluate simple expression in infix
# notation.
#######################################################################

from arpeggio import *
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _

def number():     return _(r'\d*\.\d*|\d+')
def factor():     return Optional(["+","-"]), [number,
                          ("(", expression, ")")]
def term():       return factor, ZeroOrMore(["*","/"], factor)
def expression(): return term, ZeroOrMore(["+", "-"], term)
def calc():       return OneOrMore(expression), EndOfFile


# Semantic actions
class ToFloat(SemanticAction):
    """
    Converts node value to float.
    """
    def first_pass(self, parser, node, children):
        print "Converting %s." % node.value
        return float(node.value)

class Factor(SemanticAction):
    """
    Removes parenthesis if exists and returns what was contained inside.
    """
    def first_pass(self, parser, node, children):
        print "Factor %s" % children
        if len(children) == 1:
            return children[0]
        sign = -1 if children[0] == '-' else 1
        next = 0
        if children[0] in ['+', '-']:
            next = 1
        if children[next] == '(':
            return sign * children[next+1]
        else:
            return sign * children[next]

class Term(SemanticAction):
    """
    Divides or multiplies factors.
    Factor nodes will be already evaluated.
    """
    def first_pass(self, parser, node, children):
        print "Term %s" % children
        term = children[0]
        for i in range(2, len(children), 2):
            if children[i-1]=="*":
                term *= children[i]
            else:
                term /= children[i]
        print "Term = %f" % term
        return term

class Expr(SemanticAction):
    """
    Adds or substracts terms.
    Term nodes will be already evaluated.
    """
    def first_pass(self, parser, node, children):
        print "Expression %s" % children
        expr = 0
        start = 0
        # Check for unary + or - operator
        if str(children[0]) in "+-":
            start = 1

        for i in range(start, len(children), 2):
            if i and children[i-1]=="-":
                expr -= children[i]
            else:
                expr += children[i]

        print "Expression = %f" % expr
        return expr

class Calc(SemanticAction):
    def first_pass(self, parser, node, children):
        return children[0]

# Connecting rules with semantic actions
number.sem = ToFloat()
factor.sem = Factor()
term.sem = Term()
expression.sem = Expr()
calc.sem = Calc()

if __name__ == "__main__":

    # First we will make a parser - an instance of the calc parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = ParserPython(calc)

    # Then we export it to a dot file in order to visualise it.
    # This step is optional but it is handy for debugging purposes.
    # We can make a png out of it using dot (part of graphviz) like this
    # dot -O -Tpng calc_parse_tree_model.dot
    PMDOTExporter().exportFile(parser.parser_model, "calc_parse_tree_model.dot")

    # An expression we want to evaluate
    input = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"

    # We create a parse tree out of textual input
    parse_tree = parser.parse(input)

    # Then we export it to a dot file in order to visualise it.
    # This is also optional.
    PTDOTExporter().exportFile(parse_tree, "calc_parse_tree.dot")

    # getASG will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be the result of the input expression.
    print "%s = %f" % (input, parser.getASG())

