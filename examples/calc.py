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
from arpeggio.export import PMDOTExport, PTDOTExport
from arpeggio import RegExMatch as _
import logging        

def number():          return _(r'\d*\.\d*|\d+')
def factor():           return [number, ("(", expression, ")")]
def term():             return factor, ZeroOrMore(["*","/"], factor)
def expression():       return Optional(["+","-"]), term, ZeroOrMore(["+", "-"], term)
def calc():             return expression, EndOfFile

# Semantic actions
class ToFloat(SemanticAction):
    '''Converts node value to float.'''
    def first_pass(self, parser, node, nodes):
        logging.debug("Converting %s." % node.value)
        return float(node.value)        

class Factor(SemanticAction):
    '''Removes parenthesis if exists and returns what was contained inside.'''
    def first_pass(self, parser, node, nodes):
        logging.debug("Factor %s" % nodes)
        if nodes[0] == "(":
            return nodes[1]
        else:
            return nodes[0]
        
class Term(SemanticAction):
    '''
    Divides or multiplies factors.
    Factor nodes will be already evaluated.
    '''
    def first_pass(self, parser, node, nodes):
        logging.debug("Term %s" % nodes)
        term = nodes[0]
        for i in range(2, len(nodes), 2):
            if nodes[i-1]=="*":
                term *= nodes[i]
            else:
                term /= nodes[i]
        logging.debug("Term = %f" % term)
        return term
                
class Expr(SemanticAction):
    '''
    Adds or substracts terms.
    Term nodes will be already evaluated.
    '''
    def first_pass(self, parser, node, nodes):
        logging.debug("Expression %s" % nodes)
        expr = 0
        start = 0
        # Check for unary + or - operator
        if str(nodes[0]) in "+-":
            start = 1
        
        for i in range(start, len(nodes), 2):
            if i and nodes[i-1]=="-":
                expr -= nodes[i]
            else:
                expr += nodes[i]
        
        logging.debug("Expression = %f" % expr)
        return expr
    
class Calc(SemanticAction):
    def first_pass(self, parser, node, nodes):
        return nodes[0]
    
# Connecting rules with semantic actions
number.sem = ToFloat()
factor.sem = Factor()
term.sem = Term()
expression.sem = Expr()
calc.sem = Calc()

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.DEBUG)

        # First we will make a parser - an instance of the calc parser model.
        # Parser model is given in the form of python constructs therefore we 
        # are using ParserPython class.
        parser = ParserPython(calc)

        # Then we export it to a dot file in order to visualise it. This is
        # particularly handy for debugging purposes.
        # We can make a jpg out of it using dot (part of graphviz) like this
        # dot -O -Tjpg calc_parse_tree_model.dot
        PMDOTExport().exportFile(parser.parser_model,
                        "calc_parse_tree_model.dot")
                
        # An expression we want to evaluate
        input = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"
        
        # We create a parse tree or abstract syntax tree out of textual input
        parse_tree = parser.parse(input)
        
        # Then we export it to a dot file in order to visualise it.
        PTDOTExport().exportFile(parse_tree,
                        "calc_parse_tree.dot")

        # getASG will start semantic analysis.
        # In this case semantic analysis will evaluate expression and
        # returned value will be the result of the input expression.
        print "%s = %f" % (input, parser.getASG())
        
    except NoMatch, e:
        print "Expected %s at position %s." % (e.value, str(e.parser.pos_to_linecol(e.position)))
