#######################################################################
# Name: test_optional_in_choice
# Purpose: Optional matches always succeeds but should not stop alternative
#          probing on failed match.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import pytest

# Grammar
from arpeggio import EOF, NoMatch, Optional, ParserPython


def g():    return [Optional('first'), Optional('second'), Optional('third')], EOF


def test_optional_in_choice():
    parser = ParserPython(g)
    # This input fails as the ordered choice will succeed on the first optional
    # without consuming the input.
    input_str = "second"
    with pytest.raises(NoMatch) as e:
        parser.parse(input_str)

    assert "Expected 'first' or EOF" in str(e.value)
