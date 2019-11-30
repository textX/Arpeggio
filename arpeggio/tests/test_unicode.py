#######################################################################
# Name: test_unicode
# Purpose: Tests matching unicode characters
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
    return first, "±", second


def first():
    return "♪"


def second():
    return "a"


def test_unicode_match():
    parser = ParserPython(grammar)

    parse_tree = parser.parse("♪ ± a")
    assert parse_tree
