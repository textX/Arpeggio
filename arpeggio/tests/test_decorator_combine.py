# -*- coding: utf-8 -*-
#######################################################################
# Name: test_decorator_combine
# Purpose: Test for Combine decorator. Combine decorator
#           results in Terminal parse tree node. Whitespaces are
#           preserved  (they are not skipped) and comments are not matched.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, ZeroOrMore, OneOrMore, NonTerminal, \
    Terminal, NoMatch, Combine


def test_combine_python():

    # This will result in NonTerminal node
    def root():
        return my_rule(), "."

    # This will result in Terminal node
    def my_rule():
        return Combine(ZeroOrMore("a"), OneOrMore("b"))

    parser = ParserPython(root)

    input1 = "abbb."

    # Whitespaces are preserved in lexical rules so the following input
    # should not be recognized.
    input2 = "a b bb."

    ptree1 = parser.parse(input1)

    with pytest.raises(NoMatch):
        parser.parse(input2)

    assert isinstance(ptree1, NonTerminal)
    assert isinstance(ptree1[0], Terminal)
    assert ptree1[0].value == "abbb"
