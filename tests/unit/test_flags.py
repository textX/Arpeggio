# -*- coding: utf-8 -*-
#######################################################################
# Name: test_flags
# Purpose: Test for parser flags
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import re
import pytest

# Grammar
from arpeggio import ParserPython, Optional, EOF
from arpeggio import RegExMatch as _
from arpeggio import NoMatch


def foo():      return 'r', bar, Optional(qux), baz, Optional(ham), Optional(buz), EOF
def bar():      return 'BAR'
def baz():      return _(r'1\w+')
def buz():      return _(r'Aba*', ignore_case=True)
def qux():      return _(r'/\*.*\*/', multiline=True)
def ham():      return _(r'/\*.*\*/', re_flags=re.DOTALL)  # equivalent to qux


@pytest.fixture
def parser_ci():
    return ParserPython(foo, ignore_case=True)


@pytest.fixture
def parser_nonci():
    return ParserPython(foo, ignore_case=False)


def test_parse_tree_ci(parser_ci):
    input_str = "R bar 1baz"
    parse_tree = parser_ci.parse(input_str)
    assert parse_tree is not None


def test_parse_tree_nonci(parser_nonci):
    input_str = "R bar 1baz"
    with pytest.raises(NoMatch):
        parser_nonci.parse(input_str)


def test_flags_override(parser_nonci):
    # Parser is not case insensitive
    # But the buz match is.
    input_str = "r BAR 1baz abaaaaAAaaa"
    parse_tree = parser_nonci.parse(input_str)
    assert parse_tree is not None


def test_multiline_comment(parser_nonci):
    input_str = "r BAR /*1baz\nabaaaaAAaaa\n*/1baz"
    parse_tree = parser_nonci.parse(input_str)
    assert parse_tree is not None


def test_multiline_comment_by_re_flags(parser_nonci):
    input_str = "r BAR 1baz/*this\nis\nnot\nparsed*/"
    parse_tree = parser_nonci.parse(input_str)
    assert parse_tree is not None
