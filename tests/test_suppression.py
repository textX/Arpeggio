#######################################################################
# Name: test_suppression
# Purpose: Test suppresion of parse tree nodes.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

# proj
from arpeggio import *


def test_sequence_suppress():
    """
    """

    def grammar():
        return Sequence("one", "two", "three", suppress=True), "four"

    parser = ParserPython(grammar)

    result = parser.parse("one two three four")
    assert result[0] == "four"
