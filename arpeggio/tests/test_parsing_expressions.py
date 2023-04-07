# -*- coding: utf-8 -*-
#######################################################################
# Name: test_parsing_expressions
# Purpose: Test for parsing expressions.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014-2017 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, UnorderedGroup, ZeroOrMore, OneOrMore, \
    NoMatch, EOF, Optional, And, Not, StrMatch, RegExMatch


def test_sequence():

    def grammar():
        return ("a", "b", "c")

    parser = ParserPython(grammar)

    parsed = parser.parse("a b c")

    assert str(parsed) == "a | b | c"
    assert repr(parsed) == "[  'a' [0],  'b' [2],  'c' [4] ]"


def test_ordered_choice():

    def grammar():
        return ["a", "b", "c"], EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("b")

    assert str(parsed) == "b | "
    assert repr(parsed) == "[  'b' [0], EOF [1] ]"

    parsed = parser.parse("c")
    assert str(parsed) == "c | "
    assert repr(parsed) == "[  'c' [0], EOF [1] ]"

    with pytest.raises(NoMatch) as e:
        parser.parse("ab")
    assert (
       "Expected EOF at position (1, 2) => 'a*b'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("bb")
    assert (
       "Expected EOF at position (1, 2) => 'b*b'."
    ) == str(e.value)


def test_unordered_group():
    def grammar():
        return UnorderedGroup("a", "b", "c"), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("b a c")

    assert str(parsed) == "b | a | c | "
    assert repr(parsed) == "[  'b' [0],  'a' [2],  'c' [4], EOF [5] ]"

    with pytest.raises(NoMatch) as e:
        parser.parse("a b a c")
    assert (
       "Expected 'c' at position (1, 5) => 'a b *a c'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a c")
    assert (
       "Expected 'b' at position (1, 4) => 'a c*'."
    ) == str(e.value)

    # FIXME: This test looks strange. The expectation would rather be:
    # Expected 'a' or 'c' at position (1, 3)
    with pytest.raises(NoMatch):
        parser.parse("b b a c")
    assert (
       "Expected 'b' at position (1, 4) => 'b b* a c'."
    ) == str(e.value)


def test_unordered_group_with_separator():

    def grammar():
        return UnorderedGroup("a", "b", "c", sep=StrMatch(",")), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("b, a , c")

    assert str(parsed) == "b | , | a | , | c | "
    assert repr(parsed) == \
        "[  'b' [0],  ',' [1],  'a' [3],  ',' [5],  'c' [7], EOF [8] ]"

    with pytest.raises(NoMatch) as e:
        parser.parse("a, b, a, c")
    assert (
       "Expected 'c' at position (1, 7) => 'a, b, *a, c'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a, c")
    assert (
       "Expected ',' or 'b' at position (1, 5) => 'a, c*'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("b, b, a, c")
    assert (
       "Expected 'a' or 'c' at position (1, 4) => 'b, *b, a, c'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse(",a, b, c")
    assert (
       "Expected 'a' or 'b' or 'c' at position (1, 1) => '*,a, b, c'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a, b, c,")
    assert (
       "Expected EOF at position (1, 8) => 'a, b, c*,'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a, ,b, c")
    assert (
       "Expected 'b' or 'c' at position (1, 4) => 'a, *,b, c'."
    ) == str(e.value)


def test_unordered_group_with_optionals():

    def grammar():
        return UnorderedGroup("a", Optional("b"), "c"), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("b a c")
    assert str(parsed) == "b | a | c | "

    parsed = parser.parse("a c b")
    assert str(parsed) == "a | c | b | "

    parsed = parser.parse("a c")
    assert str(parsed) == "a | c | "

    with pytest.raises(NoMatch) as e:
        parser.parse("a b c b")
    assert (
       "Expected EOF at position (1, 7) => 'a b c *b'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a b ")
    assert (
       "Expected 'c' at position (1, 5) => 'a b *'."
    ) == str(e.value)


def test_unordered_group_with_optionals_and_separator():

    def grammar():
        return UnorderedGroup("a", Optional("b"), "c", sep=","), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("b, a, c")
    assert parsed

    parsed = parser.parse("a, c, b")
    assert parsed

    parsed = parser.parse("a, c")
    assert parsed

    with pytest.raises(NoMatch) as e:
        parser.parse("a, b, c, b")
    assert (
       "Expected EOF at position (1, 8) => 'a, b, c*, b'."
    ) == str(e.value)

    # FIXME: This looks strange. Shouldn't this expect ',' (and also 'c')?
    with pytest.raises(NoMatch):
        parser.parse("a, b ")
    assert (
       "Expected EOF at position (1, 8) => 'a, b *'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a, c, ")
    assert (
       "Expected 'b' at position (1, 7) => 'a, c, *'."
    ) == str(e.value)

    # FIXME: This looks strange. Shouldn't be ',' at position 6?
    with pytest.raises(NoMatch):
        parser.parse("a, b c ")
    assert (
       "Expected 'b' at position (1, 7) => 'a, b c* '."
    ) == str(e.value)

    # FIXME: Should the separators work before the unordered group?
    with pytest.raises(NoMatch):
        parser.parse(",a, c ")
    assert (
       "Expected 'b' at position (1, 7) => ',a, c *'."
    ) == str(e.value)


def test_zero_or_more():

    def grammar():
        return ZeroOrMore("a"), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("aaaaaaa")

    assert str(parsed) == "a | a | a | a | a | a | a | "
    assert repr(parsed) == "[  'a' [0],  'a' [1],  'a' [2],"\
        "  'a' [3],  'a' [4],  'a' [5],  'a' [6], EOF [7] ]"

    parsed = parser.parse("")

    assert str(parsed) == ""
    assert repr(parsed) == "[ EOF [0] ]"

    with pytest.raises(NoMatch) as e:
        parser.parse("bbb")
    assert (
       "Expected 'a' or EOF at position (1, 1) => '*bbb'."
    ) == str(e.value)


def test_zero_or_more_with_separator():

    def grammar():
        return ZeroOrMore("a", sep=","), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("a, a , a , a ,  a,a, a")

    assert str(parsed) == \
        "a | , | a | , | a | , | a | , | a | , | a | , | a | "
    assert repr(parsed) == \
        "[  'a' [0],  ',' [1],  'a' [3],  ',' [5],  'a' [7],  ',' [9],  "\
        "'a' [11],  ',' [13],  'a' [16],  ',' [17],  'a' [18],  ',' [19],"\
        "  'a' [21], EOF [22] ]"

    parsed = parser.parse("")

    assert str(parsed) == ""
    assert repr(parsed) == "[ EOF [0] ]"

    with pytest.raises(NoMatch) as e:
        parser.parse("aa a")
    assert (
       "Expected ',' or EOF at position (1, 2) => 'a*a a'."
    ) == str(e.value)

    # FIXME: This looks strange. Can separator be before the first element?
    with pytest.raises(NoMatch):
        parser.parse(",a,a ,a")
    assert (
       "Expected ',' or EOF at position (1, 2) => ',*a,a ,a'."
    ) == str(e.value)

    # FIXME: The position looks strange.
    # Should this be 'a' or 'EOF' at the position of the last comma?
    with pytest.raises(NoMatch):
        parser.parse("a,a ,a,")
    assert (
       "Expected ',' or EOF at position (1, 2) => 'a*,a ,a,'."
    ) == str(e.value)

    # FIXME: Shouldn't this be 'a' or 'EOF' at (1, 1)?
    with pytest.raises(NoMatch):
        parser.parse("bbb")
    assert (
       "Expected ',' or EOF at position (1, 2) => 'b*bb'."
    ) == str(e.value)


def test_zero_or_more_with_optional_separator():

    def grammar():
        return ZeroOrMore("a", sep=RegExMatch(",?")), EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("a, a , a   a ,  a,a, a")

    assert str(parsed) == \
        "a | , | a | , | a | a | , | a | , | a | , | a | "
    assert repr(parsed) == \
        "[  'a' [0],  ',' [1],  'a' [3],  ',' [5],  'a' [7],  "\
        "'a' [11],  ',' [13],  'a' [16],  ',' [17],  'a' [18],  ',' [19],"\
        "  'a' [21], EOF [22] ]"

    parsed = parser.parse("")

    assert str(parsed) == ""
    assert repr(parsed) == "[ EOF [0] ]"

    parser.parse("aa a")

    with pytest.raises(NoMatch) as e:
        parser.parse(",a,a ,a")
    assert (
       "Expected 'a' or EOF at position (1, 1) => '*,a,a ,a'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a,a ,a,")
    assert (
       "Expected 'a' at position (1, 8) => 'a,a ,a,*'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("bbb")
    assert (
       "Expected 'a' or EOF at position (1, 1) => '*bbb'."
    ) == str(e.value)


def test_one_or_more():

    def grammar():
        return OneOrMore("a"), "b"

    parser = ParserPython(grammar)

    parsed = parser.parse("aaaaaa a  b")

    assert str(parsed) == "a | a | a | a | a | a | a | b"
    assert repr(parsed) == "[  'a' [0],  'a' [1],  'a' [2],"\
        "  'a' [3],  'a' [4],  'a' [5],  'a' [7],  'b' [10] ]"

    parser.parse("ab")

    with pytest.raises(NoMatch) as e:
        parser.parse("")
    assert (
       "Expected 'a' at position (1, 1) => '*'."
    ) == str(e.value)

    with pytest.raises(NoMatch):
        parser.parse("b")
    assert (
       "Expected 'a' at position (1, 1) => '*b'."
    ) == str(e.value)


def test_one_or_more_with_separator():

    def grammar():
        return OneOrMore("a", sep=","), "b"

    parser = ParserPython(grammar)

    parsed = parser.parse("a, a, a, a  b")

    assert str(parsed) == "a | , | a | , | a | , | a | b"
    assert repr(parsed) == \
        "[  'a' [0],  ',' [1],  'a' [3],  ',' [4],  'a' [6],  ',' [7],  "\
        "'a' [9],  'b' [12] ]"

    parser.parse("a b")

    with pytest.raises(NoMatch) as e:
        parser.parse("")
    assert (
       "Expected 'a' at position (1, 1) => '*'."
    ) == str(e.value)

    with pytest.raises(NoMatch):
        parser.parse("b")
    assert (
       "Expected 'a' at position (1, 1) => '*b'."
    ) == str(e.value)

    # FIXME: Should it be like this? Or ',' at (1, 2)?
    with pytest.raises(NoMatch):
        parser.parse("a a b")
    assert (
       "Expected 'a' at position (1, 1) => '*a a b'."
    ) == str(e.value)

    # FIXME: Should it be like this? Or ',' at (1, 2)?
    with pytest.raises(NoMatch):
        parser.parse("a a, b")
    assert (
       "Expected 'a' at position (1, 1) => '*a a, b'."
    ) == str(e.value)

    with pytest.raises(NoMatch):
        parser.parse(", a, a b")
    assert (
       "Expected 'a' at position (1, 1) => '*, a, a b'."
    ) == str(e.value)


def test_one_or_more_with_optional_separator():

    def grammar():
        return OneOrMore("a", sep=RegExMatch(",?")), "b"

    parser = ParserPython(grammar)

    parsed = parser.parse("a, a  a, a  b")

    assert str(parsed) == "a | , | a | a | , | a | b"
    assert repr(parsed) == \
        "[  'a' [0],  ',' [1],  'a' [3],  'a' [6],  ',' [7],  "\
        "'a' [9],  'b' [12] ]"

    parser.parse("a b")

    with pytest.raises(NoMatch) as e:
        parser.parse("")
    assert (
       "Expected 'a' at position (1, 1) => '*'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("b")
    assert (
       "Expected 'a' at position (1, 1) => '*b'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("a a, b")
    assert (
       "Expected 'a' at position (1, 6) => 'a a, *b'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse(", a, a b")
    assert (
       "Expected 'a' at position (1, 1) => '*, a, a b'."
    ) == str(e.value)


def test_optional():

    def grammar():
        return Optional("a"), "b", EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("ab")

    assert str(parsed) == "a | b | "
    assert repr(parsed) == "[  'a' [0],  'b' [1], EOF [2] ]"

    parsed = parser.parse("b")

    assert str(parsed) == "b | "
    assert repr(parsed) == "[  'b' [0], EOF [1] ]"

    with pytest.raises(NoMatch) as e:
        parser.parse("aab")
    assert (
       "Expected 'b' at position (1, 2) => 'a*ab'."
    ) == str(e.value)

    with pytest.raises(NoMatch) as e:
        parser.parse("")
    assert (
       "Expected 'a' or 'b' at position (1, 1) => '*'."
    ) == str(e.value)


# Syntax predicates

def test_and():

    def grammar():
        return "a", And("b"), ["c", "b"], EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("ab")
    assert str(parsed) == "a | b | "
    assert repr(parsed) == "[  'a' [0],  'b' [1], EOF [2] ]"

    # 'And' will try to match 'b' and fail so 'c' will never get matched
    with pytest.raises(NoMatch) as e:
        parser.parse("ac")
    assert (
       "Expected 'b' at position (1, 2) => 'a*c'."
    ) == str(e.value)

    # 'And' will not consume 'b' from the input so second 'b' will never match
    with pytest.raises(NoMatch) as e:
        parser.parse("abb")
    assert (
       "Expected EOF at position (1, 3) => 'ab*b'."
    ) == str(e.value)


def test_not():

    def grammar():
        return "a", Not("b"), ["b", "c"], EOF

    parser = ParserPython(grammar)

    parsed = parser.parse("ac")

    assert str(parsed) == "a | c | "
    assert repr(parsed) == "[  'a' [0],  'c' [1], EOF [2] ]"

    # Not will fail on 'b'
    with pytest.raises(NoMatch) as e:
        parser.parse("ab")
    assert (
       "Not expected input at position (1, 2) => 'a*b'."
    ) == str(e.value)

    # And will not consume 'c' from the input so 'b' will never match
    with pytest.raises(NoMatch) as e:
        parser.parse("acb")
    assert (
       "Expected EOF at position (1, 3) => 'ac*b'."
    ) == str(e.value)
