# -*- coding: utf-8 -*-
#######################################################################
# Name: test_ptnode_navigation_expressions
# Purpose: Test ParseTreeNode navigation expressions.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest  # noqa

# Grammar
from arpeggio import ParserPython, ZeroOrMore, ParseTreeNode, NonTerminal


def foo(): return "a", bar, "b", baz, bar2, ZeroOrMore(bar)
def bar(): return [bla, bum], baz, "c"
def bar2():return ZeroOrMore(bla)
def baz(): return "d"
def bla(): return "bla"
def bum(): return ["bum", "bam"]


def test_lookup_single():

    parser = ParserPython(foo, reduce_tree=False)

    result = parser.parse("a bum d c b d bla bum d c")

    # Uncomment following line to visualize the parse tree in graphviz
    # PTDOTExporter().exportFile(result, 'test_ptnode_navigation_expressions.dot')

    assert isinstance(result, ParseTreeNode)
    assert isinstance(result.bar, NonTerminal)
    # dot access
    assert result.bar.rule_name == 'bar'
    # Index access
    assert result[1].rule_name == 'bar'

    # There are six children from result
    assert len(result) == 6

    # There is two bar matched from result (at the begging and from ZeroOrMore)
    # Dot access collect all NTs from the given path
    assert len(result.bar) == 2
    # Verify position
    assert result.bar[0].position == 2
    assert result.bar[1].position == 18

    # Multilevel dot access returns all elements from all previous ones.
    # For example this returns all bum from all bar in result
    assert len(result.bar.bum) == 2
    # Verify that proper bum are returned
    assert result.bar.bum[0].rule_name == 'bum'
    assert result.bar.bum[1].position == 18

    # Access to terminal
    assert result.bar.bum[-1][0].value == 'bum'
    assert result.bar2.bla[0].value == 'bla'

    # The same for all bla from all bar2
    assert len(result.bar2.bla) == 1

    assert hasattr(result, "bar")
    assert hasattr(result, "baz")

    # Test that accessing an invalid rule name raises AttributeError
    with pytest.raises(AttributeError):
        result.unexisting
