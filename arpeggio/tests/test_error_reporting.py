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

from arpeggio import Optional, Not, ParserPython, NoMatch, EOF
from arpeggio import RegExMatch as _


def test_non_optional_precedence():
    """
    Test that all tried match at position are reported.
    """
    def grammar():
        return Optional('a'), 'b'

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch) as e:
        parser.parse('c')
    assert (
        "Expected 'a' or 'b' at position (1, 1) => '*c'."
    ) == str(e.value)
    assert (e.value.line, e.value.col) == (1, 1)

    # This grammar always succeeds due to the optional match
    def grammar():
        return ['b', Optional('a')]

    parser = ParserPython(grammar)
    parser.parse('b')
    parser.parse('c')


def test_optional_with_better_match():
    """
    Test that optional match that has gone further in the input stream
    has precedence over non-optional.
    """

    def grammar():  return [first, (Optional(second), 'six')]
    def first():    return 'one', 'two', 'three', '4'
    def second():   return 'one', 'two', 'three', 'four', 'five'

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch) as e:
        parser.parse('one two three four 5')

    assert (
       "Expected 'five' at position (1, 20) => 'hree four *5'."
    ) == str(e.value)
    assert (e.value.line, e.value.col) == (1, 20)


def test_alternative_added():
    """
    Test that matches from alternative branches at the same positiona are
    reported.
    """

    def grammar():
        return ['one', 'two'], _(r'\w+')

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch) as e:
        parser.parse('   three ident')
    assert (
       "Expected 'one' or 'two' at position (1, 4) => '   *three iden'."
    ) == str(e.value)
    assert (e.value.line, e.value.col) == (1, 4)


def test_file_name_reporting():
    """
    Test that if parser has file name set it will be reported.
    """

    def grammar():      return Optional('a'), 'b', EOF

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch) as e:
        parser.parse("\n\n   a c", file_name="test_file.peg")
    assert (
        "Expected 'b' at position test_file.peg:(3, 6) => '     a *c'."
    ) == str(e.value)
    assert (e.value.line, e.value.col) == (3, 6)


def test_comment_matching_not_reported():
    """
    Test that matching of comments is not reported.
    """

    def grammar():      return Optional('a'), 'b', EOF
    def comments():     return _(r'//.*$')

    parser = ParserPython(grammar, comments)

    with pytest.raises(NoMatch) as e:
        parser.parse('\n\n a // This is a comment \n c')
    assert (
       "Expected 'b' at position (4, 2) => 'comment   *c'."
    ) == str(e.value)
    assert (e.value.line, e.value.col) == (4, 2)


def test_not_match_at_beginning():
    """
    Test that matching of Not ParsingExpression is not reported in the
    error message.
    """

    def grammar():
        return Not('one'), _(r'\w+')

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch) as e:
        parser.parse('   one ident')
    # FIXME: It would be great to have the error reported at (1, 4) because the
    # whitespace is consumed.
    assert (
        "Not expected input at position (1, 1) => '*   one ide'."
    ) == str(e.value)


def test_not_match_as_alternative():
    """
    Test that Not is not reported if a part of OrderedChoice.
    """

    def grammar():
        return ['one', Not('two')], _(r'\w+')

    parser = ParserPython(grammar)
    parser.parse('three ident')

    with pytest.raises(NoMatch) as e:
        parser.parse('   two ident')
    assert (
        "Expected 'one' at position (1, 4) => '   *two ident'."
    ) == str(e.value)


def test_sequence_of_nots():
    """
    Test that sequence of Not rules is handled properly.
    """

    def grammar():
        return Not('one'), Not('two'), _(r'\w+')

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch) as e:
        parser.parse('   two ident')
    assert (
        "Not expected input at position (1, 4) => '   *two ident'."
    ) == str(e.value)


def test_compound_not_match():
    """
    Test a more complex Not match error reporting.
    """
    def grammar():
        return [Not(['two', 'three']), 'one', 'two'], _(r'\w+')

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch) as e:
        parser.parse('   three ident')
    assert (
        "Expected 'one' or 'two' at position (1, 4) => '   *three iden'."
    ) == str(e.value)

    parser.parse('   four ident')


def test_not_succeed_in_ordered_choice():
    """
    Test that Not can succeed in ordered choice leading to ordered choice
    to succeed.
    See: https://github.com/textX/Arpeggio/issues/96
    """

    def grammar():
        return [Not("a"), "a"], Optional("b")

    parser = ParserPython(grammar)
    parser.parse('b')


def test_reporting_newline_symbols_when_not_matched():

    # A case when a string match has newline
    def grammar():
        return "first", "\n"

    parser = ParserPython(grammar, skipws=False)

    with pytest.raises(NoMatch) as e:
        _ = parser.parse('first')

    assert (
        "Expected '\\n' at position (1, 6) => 'first*'."
    ) == str(e.value)

    # A case when regex match has newline
    from arpeggio import RegExMatch
    def grammar():
        return "first", RegExMatch("\n")

    parser = ParserPython(grammar, skipws=False)

    with pytest.raises(NoMatch) as e:
        _ = parser.parse('first')

    assert "Expected '\\n' at position (1, 6)" in str(e.value)

    # A case when the match is the root rule
    def grammar():
        return "root\nrule"

    parser = ParserPython(grammar, skipws=False)

    with pytest.raises(NoMatch) as e:
        _ = parser.parse('something')

    assert "Expected grammar at position (1, 1)" in str(e.value)
