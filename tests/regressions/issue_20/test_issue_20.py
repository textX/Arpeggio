#######################################################################
# Name: test_optional_in_choice
# Purpose: Optional matches always succeds but should not stop alternative
#          probing on failed match.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

# stdlib
from typing import Any, Tuple

# proj
from arpeggio import *


# Grammar
def g() -> Tuple[Any, ...]:
    return [Optional('first'), Optional('second'), Optional('third')], EOF


def test_optional_in_choice():
    parser = ParserPython(g)
    input_str = "second"
    parse_tree = parser.parse(input_str)
    assert parse_tree is not None
