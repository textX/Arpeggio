#######################################################################
# Name: test_reduce_tree
# Purpose: Test parse tree reduction
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

# proj
try:
    # imports for local pytest
    from ..arpeggio import *                                # type: ignore # pragma: no cover
    from ..arpeggio import RegExMatch as _                  # type: ignore # pragma: no cover
except ImportError:                                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import *                                  # type: ignore # pragma: no cover
    from arpeggio import RegExMatch as _                    # type: ignore # pragma: no cover


def grammar():
    return first, "a", second, [first, second]


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


def test_reduce_tree() -> None:

    peg_input = "34 a 3 3 b 3 b"

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(peg_input)

#    PTDOTExporter().exportFile(result, 'test_reduce_tree_pt.dot')

    assert result[0].rule_name == 'first'
    assert isinstance(result[0], NonTerminal)
    assert result[3].rule_name == 'first'
    assert result[0][0].rule_name == 'fourth'
    # Check reduction for direct OrderedChoice
    assert result[2][0].rule_name == 'third'

    parser = ParserPython(grammar, reduce_tree=True)
    result = parser.parse(peg_input)

    # PTDOTExporter().exportFile(result, 'test_reduce_tree_pt.dot')

    assert result[0].rule_name == 'fourth'
    assert isinstance(result[0], Terminal)
    assert result[3].rule_name == 'fourth'
    # Check reduction for direct OrderedChoice
    assert result[2][0].rule_name == 'third_str'
