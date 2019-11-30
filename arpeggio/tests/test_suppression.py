#######################################################################
# Name: test_suppression
# Purpose: Test suppresion of parse tree nodes.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
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


def test_sequence_suppress():
    """
    """

    def grammar():
        return Sequence("one", "two", "three", suppress=True), "four"

    parser = ParserPython(grammar)

    result = parser.parse("one two three four")
    assert result[0] == "four"
