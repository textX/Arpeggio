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
    StrMatch,
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
ONE_OR_MORE = _('(?<!\\s)\\' + ONE_OR_MORE_SYMBOL)
OPTIONAL = "?"
UNORDERED_GROUP = "#"
AND = "&"
NOT = "!"
OPEN = StrMatch("(", suppress=True)
REPETITION_DELIMITER = StrMatch("%", suppress=True)
CLOSE = StrMatch(")", suppress=True)
CALL_START = StrMatch("{", suppress=True)
CALL_END = StrMatch("}", suppress=True)
CALL_DELIMITER = StrMatch(',', suppress=True)
STATE = StrMatch('@', suppress=True)
PUSH_STATE = StrMatch('+@', suppress=True)
POP_STATE = StrMatch('-@', suppress=True)
STATE_LAYER_START = StrMatch('@(', suppress=True)
STATE_LAYER_END = StrMatch(')', suppress=True)
MODIFIERS_START = StrMatch('[', suppress=True)
MODIFIERS_END = StrMatch(']', suppress=True)


# PEG syntax rules
def peggrammar():
    return OneOrMore(rule), EOF


def rule():
    return rule_name, ASSIGNMENT, ordered_choice


def ordered_choice():
    return sequence, ZeroOrMore(ORDERED_CHOICE, sequence)


def sequence():
    return OneOrMore(full_expression)


def full_expression():
    return Optional([AND, NOT]), repeated_expression


def repeated_expression():
    return statement, Optional([
        OPTIONAL,
        ZERO_OR_MORE,
        ONE_OR_MORE,
        UNORDERED_GROUP
    ])


def statement():
    return [
        expression,
        expression_with_modifiers,
        parsing_state,
        push_parsing_state,
        pop_parsing_state,
    ]


def expression_with_modifiers():
    return parsing_expression_with_modifiers, Optional(action_calls)


def expression():
    return parsing_expression, Optional(action_calls)


def parsing_expression_with_modifiers():
    return modifiers, parsing_expression


def modifiers():
    return MODIFIERS_START, OneOrMore(modifier), MODIFIERS_END


def modifier():
    return (
        _(r'[a-zA-Z_][a-zA-Z_0-9]*'),
        StrMatch('=', suppress=True),
        [true_literal, false_literal, quoted_string],
        Optional(',', suppress=True)
    )


def true_literal():
    return 'True'


def false_literal():
    return 'False'


def parsing_expression():
    return [
        regex,
        str_match,
        (rule_crossref, Not(ASSIGNMENT)),
        grouped_parsing_expression,
        wrapped_with_state_layer,
    ]


def grouped_parsing_expression():
    return (
        OPEN,
        ordered_choice,
        [
            (
                REPETITION_DELIMITER,
                ordered_choice,
                CLOSE,
                [
                    ZERO_OR_MORE,
                    ONE_OR_MORE,
                ]
            ),
            ordered_choice,
            CLOSE,
        ]
    )


def parsing_state():
    return STATE, parsing_state_name


def push_parsing_state():
    return PUSH_STATE, parsing_state_name


def pop_parsing_state():
    return POP_STATE, parsing_state_name


def parsing_state_name():
    return _(r'[a-zA-Z_][a-zA-Z_0-9]*')


def wrapped_with_state_layer():
    return STATE_LAYER_START, ordered_choice, STATE_LAYER_END


def action_calls():
    return CALL_START, action_call, ZeroOrMore((CALL_DELIMITER, action_call)), CALL_END


def action_call():
    return OneOrMore(action_call_argument)


def action_call_argument():
    return [_(r'\w+'), quoted_string]


def quoted_string():
    return _(r'''(?s)('[^'\\]*(?:\\.[^'\\]*)*')|'''
             r'''("[^"\\]*(?:\\.[^"\\]*)*")''')


# PEG Lexical rules
def regex():
    return _(r"""(r'[^'\\]*(?:\\.[^'\\]*)*')|"""
             r'''(r"[^"\\]*(?:\\.[^"\\]*)*")''')


def rule_name():
    return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")


def rule_crossref():
    return rule_name


def str_match():
    return quoted_string()


def comment():
    return _("//.*\n", multiline=False)


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
