# -*- coding: utf-8 -*-
#######################################################################
# Name: test_parser_params
# Purpose: Test for parser parameters.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, NoMatch
import sys


def test_autokwd():
    """
    autokwd will match keywords on word boundaries.
    """
    def grammar():
        return ("one", "two", "three")

    parser = ParserPython(grammar, autokwd=True)

    # If autokwd is enabled this should parse without error.
    parser.parse("one two three")

    # But this will not parse because each word to match
    # will be, by default, tried to match as a whole word
    with pytest.raises(NoMatch):
        parser.parse("onetwothree")

    parser = ParserPython(grammar, autokwd=False)
    # If we turn off the autokwd than this will match.
    parser.parse("one two three")
    parser.parse("onetwothree")


def test_skipws():
    """
    skipws will skip whitespaces.
    """

    def grammar():
        return ("one", "two", "three")

    parser = ParserPython(grammar)

    # If skipws is on this should parse without error.
    parser.parse("one two three")

    # If not the same input will raise exception.
    parser = ParserPython(grammar, skipws=False)
    with pytest.raises(NoMatch):
        parser.parse("one two three")


def test_ws():
    """
    ws consists of chars that will be skipped if skipws is enables.
    By default it consists of space, tab and newline.
    """

    def grammar():
        return ("one", "two", "three")

    parser = ParserPython(grammar)

    # With default ws this should parse without error
    parser.parse("""one
                  two   three""")

    # If we make only a space char to be ws than the
    # same input will raise exception.
    parser = ParserPython(grammar, ws=" ")
    with pytest.raises(NoMatch):
        parser.parse("""one
                  two   three""")

    # But if only spaces are between words than it will
    # parse.
    parser.parse("one two  three")


def test_file(capsys):
    """
    'file' specifies an output file for the DebugPrinter mixin.
    """

    def grammar():
        return ("one", "two", "three")

    # First use stdout
    parser = ParserPython(grammar, debug=True, file=sys.stdout)
    out, err = capsys.readouterr()

    parser.dprint('this is stdout')
    out, err = capsys.readouterr()
    assert out == 'this is stdout\n'
    assert err == ''

    # Now use stderr
    parser = ParserPython(grammar, debug=False, file=sys.stderr)
    out, err = capsys.readouterr()

    parser.dprint('this is stderr')
    out, err = capsys.readouterr()
    assert out == ''
    assert err == 'this is stderr\n'
