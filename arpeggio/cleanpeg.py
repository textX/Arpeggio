#######################################################################
# Name: cleanpeg.py
# Purpose: This module is a variation of the original peg.py.
#   The syntax is slightly changed to be more readable and familiar to
#   python users. It is based on the Yash's suggestion - issue 11
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@ya.ru>
# Copyright: (c) 2009-2017 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2025 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@ya.ru>
# License: MIT License
#######################################################################


from arpeggio import (
    EOF,
    Not,
    OneOrMore,
    Optional,
    ParserPython,
    ZeroOrMore,
    visit_parse_tree,
)
from arpeggio import RegExMatch as _

from .peg import ParserPEG as ParserPEGOrig
from .peg import PEGVisitor

__all__ = ['ParserPEG']

# Lexical invariants
ASSIGNMENT = "="
ORDERED_CHOICE = "/"
ZERO_OR_MORE = "*"
ONE_OR_MORE_SYMBOL = '+'
ONE_OR_MORE = _('(?<!\s)\\' + ONE_OR_MORE_SYMBOL)
OPTIONAL = "?"
UNORDERED_GROUP = "#"
AND = "&"
NOT = "!"
OPEN = "("
CLOSE = ")"
CALL_START = "{"
CALL_END = "}"
CALL_DELIMITER = ','
STATE_START = '['
STATE_END = ']'
STATE = '@'
PUSH_STATE = '+@'
POP_STATE = '-@'
STATE_LAYER_START = '@('
STATE_LAYER_END = ')'

# PEG syntax rules
def peggrammar():       return OneOrMore(rule), EOF
def rule():             return rule_name, ASSIGNMENT, ordered_choice
def ordered_choice():   return sequence, ZeroOrMore(ORDERED_CHOICE, sequence)
def sequence():         return OneOrMore(full_expression)
def operation():        return rule_crossref, calls
def full_expression():  return Optional([AND, NOT]), repeated_expression
def repeated_expression():      return expression, Optional([OPTIONAL,
                                                             ZERO_OR_MORE,
                                                             ONE_OR_MORE,
                                                             UNORDERED_GROUP])
def expression():       return [regex,
                                push_state, pop_state, wrapped_with_state_layer, state,
                                operation, rule_crossref,
                                (OPEN, ordered_choice, CLOSE),
                                str_match], Not(ASSIGNMENT)

def state():            return STATE, state_name
def push_state():       return PUSH_STATE, state_name
def pop_state():        return POP_STATE, state_name
def wrapped_with_state_layer(): return STATE_LAYER_START, ordered_choice, STATE_LAYER_END

# PEG Lexical rules
def regex():            return _(r"""(r'[^'\\]*(?:\\.[^'\\]*)*')|"""
                                 r'''(r"[^"\\]*(?:\\.[^"\\]*)*")''')
def rule_name():        return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")
def rule_crossref():    return rule_name
def str_match():        return _(r'''(?s)('[^'\\]*(?:\\.[^'\\]*)*')|'''
                                 r'''("[^"\\]*(?:\\.[^"\\]*)*")''')
def comment():          return _("//.*\n", multiline=False)

def calls():            return CALL_START, call, ZeroOrMore([CALL_DELIMITER, call]), CALL_END
def call():             return OneOrMore(call_argument)
def call_argument():    return _(r'[^\} \t,]+')

def state_name():       return _(r'[a-zA-Z_][a-zA-Z_0-9]*')


class ParserPEG(ParserPEGOrig):

    def _from_peg(self, language_def):
        parser = ParserPython(peggrammar, comment, reduce_tree=False,
                              debug=self.debug)
        parser.root_rule_name = self.root_rule_name
        parse_tree = parser.parse(language_def)

        return visit_parse_tree(parse_tree, PEGVisitor(self.root_rule_name,
                                                       self.comment_rule_name,
                                                       self.ignore_case,
                                                       debug=self.debug))
