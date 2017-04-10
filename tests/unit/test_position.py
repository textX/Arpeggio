# -*- coding: utf-8 -*-
#######################################################################
# Name: test_position
# Purpose: Test that positions in the input stream are properly calculated.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015-2017 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython


@pytest.fixture
def parse_tree():

    def grammar(): return ("first", "second", "third")

    parser = ParserPython(grammar)

    return parser.parse("   first \n\n  second   third")


def test_position(parse_tree):
    assert parse_tree[0].position == 3
    assert parse_tree[1].position == 13
    assert parse_tree[2].position == 22
    assert parse_tree.position == 3


def test_position_end(parse_tree):
    assert parse_tree[0].position_end == 8
    assert parse_tree[1].position_end == 19
    assert parse_tree[2].position_end == 27
    assert parse_tree.position_end == 27


def test_pos_to_linecol():

    def grammar(): return ("a", "b", "c")

    parser = ParserPython(grammar)

    parse_tree = parser.parse("a\n\n\n b\nc")

    a_pos = parse_tree[0].position
    assert parser.pos_to_linecol(a_pos) == (1, 1)
    b_pos = parse_tree[1].position
    assert parser.pos_to_linecol(b_pos) == (4, 2)
    c_pos = parse_tree[2].position
    assert parser.pos_to_linecol(c_pos) == (5, 1)
