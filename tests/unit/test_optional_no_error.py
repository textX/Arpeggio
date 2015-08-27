# -*- coding: utf-8 -*-
#######################################################################
# Name: test_optional_no_error
# Purpose: Test that failures in optional matches are not reported as errors.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import unicode_literals
import pytest

from arpeggio import ZeroOrMore, Optional, ParserPython, NoMatch


def test_optional_no_error():
    """
    Test that optional match failure does not show up in the NoMatch errors.
    """
    def grammar():  return Optional('a'), 'b'

    parser = ParserPython(grammar)

    try:
        parser.parse('c')
        assert False

    except NoMatch as e:
        assert "Expected 'b'" in str(e)
