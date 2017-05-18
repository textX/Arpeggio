# -*- coding: utf-8 -*-
#######################################################################
# Name: test_sequence_params
# Purpose: Test Sequence expression parameters.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, NoMatch, Sequence


def test_skipws():
    """
    skipws may be defined per Sequence.
    """

    def grammar():
        return Sequence("one", "two", "three"), "four"

    parser = ParserPython(grammar)

    # By default, skipws is True and whitespaces will be skipped.
    parser.parse("one two   three  four")

    def grammar():
        return Sequence("one", "two", "three", skipws=False), "four"

    parser = ParserPython(grammar)

    # If we disable skipws for sequence only then whitespace
    # skipping should not be done inside sequence.
    with pytest.raises(NoMatch):
        parser.parse("one two   three  four")

    # But it will be done outside of it
    parser.parse("onetwothree  four")


def test_ws():
    """
    ws can be changed per Sequence.
    """

    def grammar():
        return Sequence("one", "two", "three"), "four"

    parser = ParserPython(grammar)

    # By default, ws consists of space, tab and newline
    # So this should parse.
    parser.parse("""one
            two   three  four""")

    def grammar():
        return Sequence("one", "two", "three", ws=' '), "four"

    parser = ParserPython(grammar)

    # If we change ws per sequence and set it to space only
    # given input will raise exception
    with pytest.raises(NoMatch):
        parser.parse("""one
                two   three  four""")

    # But ws will be default outside of sequence
    parser.parse("""one two  three
        four""")

    # Test for ws with more than one char.
    def grammar():
        return Sequence("one", "two", "three", ws=' \t'), "four"

    parser = ParserPython(grammar)

    # If we change ws per sequence and set it to spaces and tabs
    # given input will raise exception
    with pytest.raises(NoMatch):
        parser.parse("one two   \nthree \t four")

    # But ws will be default outside of sequence
    parser.parse("one two  three \n\t four")

    # Inside sequence a spaces and tabs will be skipped
    parser.parse("one \t two\t three \nfour")
