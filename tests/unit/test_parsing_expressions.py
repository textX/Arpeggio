# -*- coding: utf-8 -*-
#######################################################################
# Name: test_parsing_expressions
# Purpose: Test for parsing expressions.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, ZeroOrMore, OneOrMore, NoMatch, EOF, Optional, And, Not
from arpeggio import RegExMatch as _

def test_sequence():

    def grammar():     return ("a", "b", "c")

    parser = ParserPython(grammar)

    parsed = parser.parse("a b c")

    assert str(parsed) == "a | b | c"
    assert repr(parsed) == "[  'a' [0],  'b' [2],  'c' [4] ]"

def test_ordered_choice():

    def grammar():     return ["a", "b", "c"], EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("b")

    assert str(parsed) == "b | "
    assert repr(parsed) == "[  'b' [0], EOF [1] ]"

    parsed = parser.parse("c")
    assert str(parsed) == "c | "
    assert repr(parsed) == "[  'c' [0], EOF [1] ]"

    with pytest.raises(NoMatch):
        parser.parse("ab")

    with pytest.raises(NoMatch):
        parser.parse("bb")

def test_zero_or_more():

    def grammar():     return ZeroOrMore("a"), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("aaaaaaa")

    assert str(parsed) == "a | a | a | a | a | a | a | "
    assert repr(parsed) == "[  'a' [0],  'a' [1],  'a' [2],  'a' [3],  'a' [4],  'a' [5],  'a' [6], EOF [7] ]"

    parsed = parser.parse("")

    assert str(parsed) == ""
    assert repr(parsed) == "[ EOF [0] ]"

    with pytest.raises(NoMatch):
        parser.parse("bbb")

def test_one_or_more():

    def grammar():      return OneOrMore("a"), "b"

    parser = ParserPython(grammar)

    parsed = parser.parse("aaaaaa a  b")

    assert str(parsed) == "a | a | a | a | a | a | a | b"
    assert repr(parsed) == "[  'a' [0],  'a' [1],  'a' [2],  'a' [3],  'a' [4],  'a' [5],  'a' [7],  'b' [10] ]"

    parser.parse("ab")

    with pytest.raises(NoMatch):
        parser.parse("")

    with pytest.raises(NoMatch):
        parser.parse("b")

def test_optional():

    def grammar():      return Optional("a"), "b", EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("ab")

    assert str(parsed) == "a | b | "
    assert repr(parsed) == "[  'a' [0],  'b' [1], EOF [2] ]"

    parsed = parser.parse("b")

    assert str(parsed) == "b | "
    assert repr(parsed) == "[  'b' [0], EOF [1] ]"

    with pytest.raises(NoMatch):
        parser.parse("aab")

    with pytest.raises(NoMatch):
        parser.parse("")


# Syntax predicates

def test_and():

    def grammar():      return "a", And("b"), ["c", "b"], EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("ab")
    assert str(parsed) == "a | b | "
    assert repr(parsed) == "[  'a' [0],  'b' [1], EOF [2] ]"

    # 'And' will try to match 'b' and fail so 'c' will never get matched
    with pytest.raises(NoMatch):
        parser.parse("ac")

    # 'And' will not consume 'b' from the input so second 'b' will never match
    with pytest.raises(NoMatch):
        parser.parse("abb")

def test_not():

    def grammar():      return "a", Not("b"), ["b", "c"], EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("ac")

    assert str(parsed) == "a | c | "
    assert repr(parsed) == "[  'a' [0],  'c' [1], EOF [2] ]"

    # Not will will fail on 'b'
    with pytest.raises(NoMatch):
        parser.parse("ab")

    # And will not consume 'c' from the input so 'b' will never match
    with pytest.raises(NoMatch):
        parser.parse("acb")

