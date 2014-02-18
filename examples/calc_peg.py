#######################################################################
# Name: calc_peg.py
# Purpose: Simple expression evaluator example using PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example is functionally equivalent to calc.py. The difference is that
# in this example grammar is specified using PEG language instead of python constructs.
# Semantic actions are used to calculate expression during semantic
# analysis.
# Parser model as well as parse tree exported to dot files should be
# the same as parser model and parse tree generated in calc.py example.
#######################################################################

from arpeggio import *
from arpeggio.peg import ParserPEG
from arpeggio.export import PMDOTExporter, PTDOTExporter

# Semantic actions
from calc import ToFloat, Factor, Term, Expr, Calc

# Grammar is defined using textual specification based on PEG language.
calc_grammar = """
        number <- r'\d*\.\d*|\d+';
        factor <- ("+" / "-")?
                  (number / "(" expression ")");
        term <- factor (( "*" / "/") factor)*;
        expression <- term (("+" / "-") term)*;
        calc <- expression+ EndOfFile;
"""

# Rules are mapped to semantic actions
sem_actions = {
    "number" : ToFloat(),
    "factor" : Factor(),
    "term"   : Term(),
    "expression" : Expr(),
    "calc"   : Calc()
}


# First we will make a parser - an instance of the calc parser model.
# Parser model is given in the form of PEG notation therefore we
# are using ParserPEG class. Root rule name (parsing expression) is "calc".
parser = ParserPEG(calc_grammar, "calc", debug=True)


# Then we export it to a dot file.
PMDOTExporter().exportFile(parser.parser_model, "calc_peg_parser_model.dot")

# An expression we want to evaluate
input = "-(4-1)*5+(2+4.67)+5.89/(.2+7)"

# Then parse tree is created out of the input expression.
parse_tree = parser.parse(input)

# We save it to dot file in order to visualise it.
PTDOTExporter().exportFile(parse_tree, "calc_peg_parse_tree.dot")

# getASG will start semantic analysis.
# In this case semantic analysis will evaluate expression and
# returned value will be evaluated result of the input expression.
# Semantic actions are supplied to the getASG function.
print "%s = %f" % (input, parser.getASG(sem_actions))

