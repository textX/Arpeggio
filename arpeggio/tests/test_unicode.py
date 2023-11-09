#######################################################################
# Name: test_unicode
# Purpose: Tests matching unicode characters
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import pytest  # noqa

# Grammar
from arpeggio import ParserPython

def grammar():      return first, "±", second
def first():        return "♪"
def second():       return "a"


def test_unicode_match():
    parser = ParserPython(grammar)

    parse_tree = parser.parse("♪ ± a")
    assert parse_tree
