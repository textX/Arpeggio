# -*- coding: utf-8 -*-
#######################################################################
# Name: test_pos_to_linecol
# Purpose: Test that position in the input stream is properly converted
#          to line,col.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython

def test_pos_to_linecol():

    def grammar():     return ("a", "b", "c")

    parser = ParserPython(grammar)

    parse_tree = parser.parse("a\n\n\n b\nc")

    a_pos = parse_tree[0].position
    assert parser.pos_to_linecol(a_pos) == (1, 1)
    b_pos = parse_tree[1].position
    assert parser.pos_to_linecol(b_pos) == (4, 2)
    c_pos = parse_tree[2].position
    assert parser.pos_to_linecol(c_pos) == (5, 1)


