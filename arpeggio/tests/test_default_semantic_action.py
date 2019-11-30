#######################################################################
# Name: test_default_semantic_action
# Purpose: Default semantic action is applied during semantic analysis
#           if no action is given for node type. Default action converts
#           terminals to strings, remove StrMatch terminals from sequences.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

# stdlib
from typing import Any, List

# proj
try:
    # imports for local pytest
    from ..arpeggio import *    # type: ignore # pragma: no cover
    from ..arpeggio import RegExMatch as _  # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import *       # type: ignore # pragma: no cover
    from arpeggio import RegExMatch as _  # type: ignore # pragma: no cover


def grammar() -> Any:
    return parentheses, 'strmatch'


def parentheses() -> Any:
    return '(', rulea, ')'


def rulea() -> Any:
    return ['+', '-'], number


def number() -> Any:
    return _(r'\d+')


p_removed = False
number_str = False
parse_tree_node = False


class ParenthesesSA(SemanticAction):
    def first_pass(self, parser: ParserPython, node: ParseTreeNode, children: List[Any]) -> Any:
        global p_removed, parse_tree_node
        p_removed = str(children[0]) != '('
        parse_tree_node = isinstance(children[0], ParseTreeNode)
        return children[0] if len(children) == 1 else children[1]


class RuleSA(SemanticAction):
    def first_pass(self, parser: ParserPython, node: ParseTreeNode, children: List[Any]) -> Any:
        global number_str
        number_str = type(children[1]) == str
        return children[1]


# noinspection PyTypeHints
parentheses.sem = ParenthesesSA()   # type: ignore
# noinspection PyTypeHints
rulea.sem = RuleSA()                # type: ignore


def test_default_action_enabled() -> None:

    parser = ParserPython(grammar)

    parser.parse('(-34) strmatch')

    parser.getASG(defaults=True)

    assert p_removed
    assert number_str
    assert not parse_tree_node


def test_default_action_disabled() -> None:

    parser = ParserPython(grammar)

    parser.parse('(-34) strmatch')

    parser.getASG(defaults=False)

    assert not p_removed
    assert not number_str
    assert parse_tree_node
