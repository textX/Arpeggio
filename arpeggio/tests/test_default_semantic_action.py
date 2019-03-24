# -*- coding: utf-8 -*-
#######################################################################
# Name: test_default_semantic_action
# Purpose: Default semantic action is applied during semantic analysis
#           if no action is given for node type. Default action converts
#           terminals to strings, remove StrMatch terminals from sequences.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest  # noqa
from arpeggio import ParserPython, SemanticAction, ParseTreeNode
from arpeggio import RegExMatch as _

try:
    # For python 2.x
    text=unicode
except:
    # For python 3.x
    text=str

def grammar():      return parentheses, 'strmatch'
def parentheses():  return '(', rulea, ')'
def rulea():        return ['+', '-'], number
def number():       return _(r'\d+')


p_removed = False
number_str = False
parse_tree_node = False


class ParenthesesSA(SemanticAction):
    def first_pass(self, parser, node, children):
        global p_removed, parse_tree_node
        p_removed = text(children[0]) != '('
        parse_tree_node = isinstance(children[0], ParseTreeNode)
        return children[0] if len(children) == 1 else children[1]


class RuleSA(SemanticAction):
    def first_pass(self, parser, node, children):
        global number_str
        number_str = type(children[1]) == text
        return children[1]


parentheses.sem = ParenthesesSA()
rulea.sem = RuleSA()


def test_default_action_enabled():

    parser = ParserPython(grammar)

    parser.parse('(-34) strmatch')

    parser.getASG(defaults=True)

    assert p_removed
    assert number_str
    assert not parse_tree_node


def test_default_action_disabled():

    parser = ParserPython(grammar)

    parser.parse('(-34) strmatch')

    parser.getASG(defaults=False)

    assert not p_removed
    assert not number_str
    assert parse_tree_node
