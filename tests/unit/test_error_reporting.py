# -*- coding: utf-8 -*-
#######################################################################
# Name: test_error_reporting
# Purpose: Test error reporting for various cases.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import unicode_literals
import pytest

from arpeggio import ZeroOrMore, Optional, ParserPython, NoMatch, EOF


def test_non_optional_precedence():
    """
    Test that non-optional match has precedence over optional.
    """
    def grammar():  return Optional('a'), 'b'

    parser = ParserPython(grammar)

    try:
        parser.parse('c')

    except NoMatch as e:
        assert "Expected 'b'" in str(e)

    def grammar():  return ['b', Optional('a')]

    parser = ParserPython(grammar)

    try:
        parser.parse('c')

    except NoMatch as e:
        assert "Expected 'b'" in str(e)

def test_optional_with_better_match():
    """
    Test that optional match that has gone further in the input stream
    has precedence over non-optional.
    """

    def grammar():  return [first, Optional(second)]
    def first():    return 'one', 'two', 'three', '4'
    def second():   return 'one', 'two', 'three', 'four', 'five'

    parser = ParserPython(grammar)

    try:
        parser.parse('one two three four 5')

    except NoMatch as e:
        assert "Expected 'five'" in str(e)


