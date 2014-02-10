#######################################################################
# Name: simple.py
# Purpose: Simple language based on example from pyPEG
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example demonstrates grammar definition using python constructs.
# It is taken and adapted from pyPEG project (see http://www.fdik.org/pyPEG/).
#######################################################################

from arpeggio import *
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _

def comment():          return [_("//.*"), _("/\*.*\*/")]
def literal():          return _(r'\d*\.\d*|\d+|".*?"')
def symbol():           return _(r"\w+")
def operator():         return _(r"\+|\-|\*|\/|\=\=")
def operation():        return symbol, operator, [literal, functioncall]
def expression():       return [literal, operation, functioncall]
def expressionlist():   return expression, ZeroOrMore(",", expression)
def returnstatement():  return Kwd("return"), expression
def ifstatement():      return Kwd("if"), "(", expression, ")", block, Kwd("else"), block
def statement():        return [ifstatement, returnstatement], ";"
def block():            return "{", OneOrMore(statement), "}"
def parameterlist():    return "(", symbol, ZeroOrMore(",", symbol), ")"
def functioncall():     return symbol, "(", expressionlist, ")"
def function():         return Kwd("function"), symbol, parameterlist, block
def simpleLanguage():   return function

try:

    # Parser instantiation. simpleLanguage is the definition of the root rule
    # and comment is a grammar rule for comments.
    parser = ParserPython(simpleLanguage, comment, debug=True)

    # We save parser model to dot file in order to visualise it.
    # We can make a png out of it using dot (part of graphviz) like this
    # dot -Tpng -O simple_parser.dot
    PMDOTExporter().exportFile(parser.parser_model,
            "simple_parser_model.dot")

    # Parser model for comments is handled as separate model
    PMDOTExporter().exportFile(parser.comments_model,
            "simple_parser_comments.dot")

    input = """
        function fak(n) {
            if (n==0) {
                // For 0! result is 0
                return 0;
            } else { /* And for n>0 result is calculated recursively */
                return n * fak(n - 1);
            };
        }
    """
    parse_tree = parser.parse(input)

    PTDOTExporter().exportFile(parse_tree,
            "simple_parse_tree.dot")

except NoMatch, e:
    print "Expected %s at position %s." % (e.value, str(e.parser.pos_to_linecol(e.position)))
