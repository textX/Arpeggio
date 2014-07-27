# -*- coding: utf-8 -*-
#######################################################################
# Name: test_peg_parser
# Purpose: Test for parser constructed using PEG textual grammars.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import pytest

# Grammar
from arpeggio import ParserPython, ZeroOrMore


def foo(): return "a", bar, "b", baz
def bar(): return "c"
def baz(): return "d"


def test_lookup_single():

    parser = ParserPython(foo)

    result = parser.parse("a c b d")

    assert hasattr(result, "bar")
    assert hasattr(result, "baz")
    assert not hasattr(result, "unexisting")

