# -*- coding: utf-8 -*-
#######################################################################
# Name: test_python_parser
# Purpose: Test for parser constructed using Python-based grammars.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest  # noqa

# Grammar
from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, ParserPython,\
    Sequence, NonTerminal
from arpeggio import RegExMatch as _


def number():     return _(r'\d*\.\d*|\d+')
def factor():     return Optional(["+", "-"]), [number,
                                                ("(", expression, ")")]
def term():       return factor, ZeroOrMore(["*", "/"], factor)
def expression(): return term, ZeroOrMore(["+", "-"], term)
def calc():       return OneOrMore(expression), EOF


def test_pp_construction():
    '''
    Tests parser construction from python internal DSL description.
    '''
    parser = ParserPython(calc)

    assert parser.parser_model.rule_name == 'calc'
    assert isinstance(parser.parser_model, Sequence)
    assert parser.parser_model.nodes[0].desc == 'OneOrMore'


def test_parse_input():

    parser = ParserPython(calc)
    input = "4+5*7/3.45*-45*(2.56+32)/-56*(2-1.34)"
    result = parser.parse(input)

    assert isinstance(result, NonTerminal)
    assert str(result) == "4 | + | 5 | * | 7 | / | 3.45 | * | - | 45 | * | ( | 2.56 | + | 32 | ) | / | - | 56 | * | ( | 2 | - | 1.34 | ) | "
    assert repr(result) == "[ [ [ [ number '4' [0] ] ],  '+' [1], [ [ number '5' [2] ],  '*' [3], [ number '7' [4] ],  '/' [5], [ number '3.45' [6] ],  '*' [10], [  '-' [11], number '45' [12] ],  '*' [14], [  '(' [15], [ [ [ number '2.56' [16] ] ],  '+' [20], [ [ number '32' [21] ] ] ],  ')' [23] ],  '/' [24], [  '-' [25], number '56' [26] ],  '*' [28], [  '(' [29], [ [ [ number '2' [30] ] ],  '-' [31], [ [ number '1.34' [32] ] ] ],  ')' [36] ] ] ], EOF [37] ]"

