# -*- coding: utf-8 -*-
#######################################################################
# Name: test_error_reporting_verbose
# Purpose: Test error reporting for various cases when verbose=True enabled.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import unicode_literals
import pytest

from arpeggio import Optional, Not, ParserPython, NoMatch, EOF, Sequence, RegExMatch, StrMatch, OrderedChoice
from arpeggio import RegExMatch as _


def test_optional_with_better_match():
    """
    Test that optional match that has gone further in the input stream
    has precedence over non-optional.
    """

    def grammar():  return [first, (Optional(second), 'six')]
    def first():    return 'one', 'two', 'three', '4'
    def second():   return 'one', 'two', 'three', 'four', 'five'

    parser = ParserPython(grammar, verbose=True)
    assert parser.verbose

    with pytest.raises(NoMatch) as e:
        parser.parse('one two three four 5')

    assert (
        "Expected "
        "'six' at position (1, 1) or "
        "'4' at position (1, 15) or "
        "'five' at position (1, 20) => "
        "'hree four *5'."
    ) == str(e.value)
    assert (e.value.line, e.value.col) == (1, 20)
