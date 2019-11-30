#######################################################################
# Name: test_semantic_action_results
# Purpose: Tests semantic actions based on visitor
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

# proj
try:
    # imports for local pytest
    from ..arpeggio import *                                # type: ignore # pragma: no cover
    from ..arpeggio import RegExMatch as _                  # type: ignore # pragma: no cover
    from ..export import PTDOTExporter                      # type: ignore # pragma: no cover
except ImportError:                                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import *                                  # type: ignore # pragma: no cover
    from arpeggio import RegExMatch as _                    # type: ignore # pragma: no cover
    from ..export import PTDOTExporter                      # type: ignore # pragma: no cover


def grammar():
    return first, "a", second


def first():
    return [fourth, third], ZeroOrMore(third)


def second():
    return OneOrMore(third), "b"


def third():
    return [third_str, fourth]


def third_str():
    return "3"


def fourth():
    return _(r'\d+')


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


def test_semantic_action_results() -> None:

    global first_sar, third_sar

    peg_input = "4 3 3 3 a 3 3 b"

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(peg_input)

    PTDOTExporter().exportFile(result, 'test_semantic_action_results_pt.dot')

    visit_parse_tree(result, Visitor(defaults=True))

    assert isinstance(first_sar, SemanticActionResults)
    assert len(first_sar.third) == 3
    assert third_sar.third_str[0] == '3'    # type: ignore
