# -*- coding: utf-8 -*-
#######################################################################
# Name: test_reduce_tree
# Purpose: Test parse tree reduction
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
from copy import deepcopy
import pytest  # noqa

# Grammar
from arpeggio import ZeroOrMore, OneOrMore, ParserPython, NonTerminal
from arpeggio import RegExMatch as _


def grammar():      return first, "a", second, [first, second]
def first():        return [fourth, third], ZeroOrMore(third)
def second():       return OneOrMore(third), "b"
def third():        return [third_str, fourth]
def third_str():    return "3"
def fourth():       return _(r'\d+')


def test_parse_tree_copy():

    input = "34 a 3 3 b 3 b"

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(input)

    result_copy = deepcopy(result)

    assert isinstance(result_copy, NonTerminal)
    assert result is not result_copy
    assert str(result) == str(result_copy)
