#######################################################################
# Name: parser_peg_clean.py
# Purpose: This module is a variation of the original visitor_peg.py.
#   The syntax is slightly changed to be more readable and familiar to
#   python users. It is based on the Yash's suggestion - issue 11
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014-2017 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

# proj
from . import parser_peg
from . import parser_python
from . import peg_expressions
from . import peg_lexical
from . import visitor_base
from . import visitor_peg


__all__ = ['ParserPEG']


# PEG syntax rules
def peggrammar():
    return peg_expressions.OneOrMore(rule), peg_expressions.EOF


def rule():
    return rule_name, peg_lexical.ASSIGNMENT, ordered_choice


def ordered_choice():
    return sequence, peg_expressions.ZeroOrMore(peg_lexical.ORDERED_CHOICE, sequence)


def sequence():
    return peg_expressions.OneOrMore(prefix)


def prefix():
    return peg_expressions.Optional([peg_lexical.AND, peg_lexical.NOT]), sufix


def sufix():
    return expression, peg_expressions.Optional([peg_lexical.OPTIONAL,
                                                 peg_lexical.ZERO_OR_MORE,
                                                 peg_lexical.ONE_OR_MORE,
                                                 peg_lexical.UNORDERED_GROUP])


def expression():
    return [regex, rule_crossref,
            (peg_lexical.OPEN, ordered_choice, peg_lexical.CLOSE),
            str_match], peg_expressions.Not(peg_lexical.ASSIGNMENT)


# PEG Lexical rules
def regex():
    return [("r'", peg_expressions.RegExMatch(r'''[^'\\]*(?:\\.[^'\\]*)*'''), "'"),
            ('r"', peg_expressions.RegExMatch(r'''[^"\\]*(?:\\.[^"\\]*)*'''), '"')]


def rule_name():
    return peg_expressions.RegExMatch(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")


def rule_crossref():
    return rule_name


def str_match():
    return peg_expressions.RegExMatch(r'''(?s)('[^'\\]*(?:\\.[^'\\]*)*')|'''
                                      r'''("[^"\\]*(?:\\.[^"\\]*)*")''')


def comment():
    return "//", peg_expressions.RegExMatch(".*\n")


class ParserPEG(parser_peg.ParserPEG):

    def _from_peg(self, language_def):
        parser = parser_python.ParserPython(peggrammar, comment, reduce_tree=False, debug=self.debug)
        parser.root_rule_name = self.root_rule_name
        parse_tree = parser.parse(language_def)
        return visitor_base.visit_parse_tree(parse_tree,
                                             visitor_peg.PEGVisitor(self.root_rule_name,
                                                                    self.comment_rule_name,
                                                                    self.ignore_case,
                                                                    debug=self.debug))
