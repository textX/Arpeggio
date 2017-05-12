# -*- coding: utf-8 -*-
#######################################################################
# Name: test_semantic_action_results
# Purpose: Tests semantic actions based on visitor
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest  # noqa

# Grammar
from arpeggio import ZeroOrMore, OneOrMore, ParserPython,\
    PTNodeVisitor, visit_parse_tree, SemanticActionResults
from arpeggio.export import PTDOTExporter
from arpeggio import RegExMatch as _

def grammar():      return first, "a", second
def first():        return [fourth, third], ZeroOrMore(third)
def second():       return OneOrMore(third), "b"
def third():        return [third_str, fourth]
def third_str():    return "3"
def fourth():       return _(r'\d+')


first_sar = None
third_sar = None


class Visitor(PTNodeVisitor):

    def visit_first(self, node, children):
        global first_sar
        first_sar = children

    def visit_third(self, node, children):
        global third_sar
        third_sar = children

        return 1


def test_semantic_action_results():

    global first_sar, third_sar

    input = "4 3 3 3 a 3 3 b"

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(input)

    PTDOTExporter().exportFile(result, 'test_semantic_action_results_pt.dot')

    visit_parse_tree(result, Visitor(defaults=True))

    assert isinstance(first_sar, SemanticActionResults)
    assert len(first_sar.third) == 3
    assert third_sar.third_str[0] == '3'
