#######################################################################
# Name: test_peg_parser
# Purpose: Test for parser constructed using PEG textual grammars.
# Authors: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@yandex.ru>
# Copyright: (c) 2025
#           Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>,
#           Andrey N. Dotsenko <pgandrey@yandex.ru>
# License: MIT License
#
# This file is originally based on test_peg_parser.py
#######################################################################

import pytest
from arpeggio.peg import ParserPEG
from arpeggio.cleanpeg import ParserPEG as ParserPEGClean

grammar = r'''
parser_entry <- program_element* EOF;

program_element <-
    function
    / function_call;

function <-
    FUNCTION_START function_name{push, add}
    program_element*
    FUNCTION_END function_name{pop};

function_call <-
    function_name{any}
    ARGUMENTS_START
    VALID_NAME?
    (
        ARGUMENTS_DELIMITER
        VALID_NAME
    )*
    ARGUMENTS_DELIMITER?
    ARGUMENTS_END;

FUNCTION_START <- 'def';
function_name <- VALID_NAME;
FUNCTION_END <- 'end of';
ARGUMENTS_START <- '(';
ARGUMENTS_END <- ')';
VALID_NAME <- r'[a-zA-Z0-9_]+';
ARGUMENTS_DELIMITER <- ',';
'''

clean_grammar = grammar.replace('<-', '=').replace(';', '')

@pytest.mark.parametrize('parser', [
    ParserPEGClean(clean_grammar, 'parser_entry'),
    ParserPEG(grammar, 'parser_entry'),
])
def test_backreference(parser):
    input = """
def function_name1
end of function_name1

def function_name2
end of function_name2
    """
    result = parser.parse(input)

@pytest.mark.parametrize('parser', [
    ParserPEGClean(clean_grammar, 'parser_entry'),
    ParserPEG(grammar, 'parser_entry'),
])
def test_backreference_any(parser):
    input = """
def function_name1
end of function_name1

def function_name2
    function_name1(arg1)
end of function_name2

function_name1(1, 2, 3)
function_name2(1, 2, 3)
"""
    result = parser.parse(input)

