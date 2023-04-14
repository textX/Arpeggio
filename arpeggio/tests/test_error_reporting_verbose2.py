# -*- coding: utf-8 -*-
#######################################################################
# Name: test_error_reporting_verbose
# Purpose: Test error reporting for various cases when verbose=True enabled.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import unicode_literals
import pytest

from arpeggio import Optional, Not, ParserPython, NoMatch, EOF, Sequence, \
    RegExMatch, StrMatch, OrderedChoice, UnorderedGroup, ZeroOrMore, OneOrMore
from arpeggio import RegExMatch as _


def test_ordered_choice():
    def grammar():
        return ["a", "b", "c"], EOF

    parser = ParserPython(grammar, verbose2=True)
    with pytest.raises(NoMatch) as e:
        parser.parse("ab")
    assert (
       "Expected:\n"
       "1:1: 'b' or 'c'\n"
       "1:2: EOF\n"
       " => 'a*b'."
    ) == str(e.value)

    parser = ParserPython(grammar, verbose2=True)
    with pytest.raises(NoMatch) as e:
        parser.parse("bb")
    assert (
       "Expected:\n"
       "1:1: 'a' or 'c'\n"
       "1:2: EOF\n"
       " => 'b*b'."
    ) == str(e.value)


def test_unordered_group_with_optionals_and_separator():
    def grammar():
        return UnorderedGroup("a", Optional("b"), "c", sep=","), EOF

    parser = ParserPython(grammar)
    with pytest.raises(NoMatch) as e:
        parser.parse("a, c, ")
    assert (
       "Expected 'b' at position (1, 7) => 'a, c, *'."
    ) == str(e.value)

    parser = ParserPython(grammar, verbose2=True)
    with pytest.raises(NoMatch) as e:
        parser.parse("a, c, ")
    assert (
       "Expected:\n"
       "1:5: EOF\n"
       "1:7: 'b'\n"
       " => 'a, c, *'."
    ) == str(e.value)


def test_zero_or_more_with_separator():
    def grammar():
        return ZeroOrMore("a", sep=","), EOF

    parser = ParserPython(grammar)
    with pytest.raises(NoMatch) as e:
        parser.parse("a,a ,a,")
    assert (
       "Expected 'a' at position (1, 8) => 'a,a ,a,*'."
    ) == str(e.value)

    parser = ParserPython(grammar, verbose2=True)
    with pytest.raises(NoMatch) as e:
        parser.parse("a,a ,a,")
    assert (
       "Expected:\n"
       "1:7: EOF\n"
       "1:8: 'a'\n"
       " => 'a,a ,a,*'."
    ) == str(e.value)


def test_zero_or_more_with_optional_separator():
    def grammar():
        return ZeroOrMore("a", sep=RegExMatch(",?")), EOF

    parser = ParserPython(grammar)
    with pytest.raises(NoMatch) as e:
        parser.parse("a,a ,a,")
    assert (
       "Expected 'a' at position (1, 8) => 'a,a ,a,*'."
    ) == str(e.value)

    parser = ParserPython(grammar, verbose2=True)
    with pytest.raises(NoMatch) as e:
        parser.parse("a,a ,a,")
    assert (
       "Expected:\n"
       "1:7: EOF\n"
       "1:8: 'a'\n"
       " => 'a,a ,a,*'."
    ) == str(e.value)


def test_one_or_more_with_optional_separator():
    def grammar():
        return OneOrMore("a", sep=RegExMatch(",?")), "b"

    parser = ParserPython(grammar)
    with pytest.raises(NoMatch) as e:
        parser.parse("a a, b")
    assert (
        "Expected 'a' at position (1, 6) => 'a a, *b'."
    ) == str(e.value)

    parser = ParserPython(grammar, verbose2=True)
    with pytest.raises(NoMatch) as e:
        parser.parse("a a, b")
    assert (
        "Expected:\n"
        "1:4: 'b'\n"
        "1:6: 'a'\n"
        " => 'a a, *b'."
    ) == str(e.value)
