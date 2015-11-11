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
from arpeggio import RegExMatch as _


def test_non_optional_precedence():
    """
    Test that all tried match at position are reported.
    """
    def grammar():  return Optional('a'), 'b'

    parser = ParserPython(grammar)

    try:
        parser.parse('c')

    except NoMatch as e:
        assert "Expected 'a' or 'b'" in str(e)

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

def test_file_name_reporting():
    """
    Test that if parser has file name set it will be reported.
    """

    def grammar():      return Optional('a'), 'b', EOF

    parser = ParserPython(grammar)

    try:
        parser.parse("\n\n   a c", file_name="test_file.peg")
    except NoMatch as e:
        assert "Expected 'b' at test_file.peg:(3, 6)" in str(e)

def test_comment_matching_not_reported():
    """
    Test that matching of comments is not reported.
    """

    def grammar():      return Optional('a'), 'b', EOF
    def comments():     return _('\/\/.*$')

    parser = ParserPython(grammar, comments)

    try:
        parser.parse('\n\n a // This is a comment \n c')
    except NoMatch as e:
        assert "Expected 'b' at position (4, 2)" in str(e)










