# -*- coding: utf-8 -*-
#######################################################################
# Name: test_suppression
# Purpose: Test suppresion of parse tree nodes.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest  # noqa
from arpeggio import ParserPython, Sequence, StrMatch, RegExMatch


def test_sequence_suppress():
    """
    """

    def grammar():
        return Sequence("one", "two", "three", suppress=True), "four"

    parser = ParserPython(grammar)

    result = parser.parse("one two three four")
    assert result[0] == "four"


def test_suppress_string_match():
    """
    Test that string matches with suppress=True do not produce parse tree
    nodes.
    """

    class SuppressStrMatch(StrMatch):
        suppress = True

    def grammar():
        return "one", "two", SuppressStrMatch("three"), "four"

    parser = ParserPython(grammar)

    result = parser.parse("one two three four")
    assert len(result) == 3
    assert result[1] == "two"
    assert result[2] == "four"


def test_register_syntax_classes_suppress():
    """
    Test suppressing by overriding special syntax forms (lists - OrderedChoice,
    tuples - Sequences and string - StrMatch).
    """

    class SuppressStrMatch(StrMatch):
        suppress = True

    def grammar():
        return "one", "two", RegExMatch(r'\d+'), "three"

    parser = ParserPython(grammar,
                          syntax_classes={'StrMatch': SuppressStrMatch})

    result = parser.parse("one two 42 three")

    # Only regex will end up in the tree
    assert len(result) == 1
    assert result[0] == "42"
