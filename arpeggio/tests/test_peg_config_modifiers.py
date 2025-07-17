#######################################################################
# Name: test_peg_actions_and_states
# Purpose: Test for parser constructed using PEG textual grammars using the actions and states system.
# Authors: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@yandex.ru>
# Copyright: (c) 2025
#           Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>,
#           Andrey N. Dotsenko <pgandrey@yandex.ru>
# License: MIT License
#
# This file is originally based on test_peg_actions_and_states.py
#######################################################################

import pytest

from arpeggio.peg import ParserPEG
from arpeggio.cleanpeg import ParserPEG as ParserPEGClean
import enum


# Functions are used instead of variables to store grammar only to make parametrized test results readable
def get_grammar():
    return r'''
parser_entry <-
    (
        INDENTATION{list append, suppress} program_element
        (INDENTATION{list last, suppress} program_element)*
    )?
    EOF;

program_element <-
    function
    / function_call;

function <-
    @(
        FUNCTION_START function_name{push}
        (
            INDENTATION{parent list longer, list append, suppress} program_element
            (INDENTATION{list last, suppress} program_element)*
        )?
        INDENTATION{parent list last, list try remove, suppress} FUNCTION_END [skip_whitespace=True, whitespace=' \t']function_name{pop}
    );


function_call <-
    function_name
    !SPACE
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
ARGUMENTS_START <- '('{suppress};
ARGUMENTS_END <- ')'{suppress};
VALID_NAME <- r'[a-zA-Z0-9_]+';
ARGUMENTS_DELIMITER <- ','{suppress};
SPACE <- [skip_whitespace=False]r'[ \t]+';
INDENTATION <- [whitespace='\n\r']r' *';
'''


def get_clean_grammar():
    return get_grammar().replace('<-', '=').replace(';', '')


class Debugging(enum.Flag):
    ENABLED = True
    DISABLED = False


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_two_modifiers_with_string_modifier_and_backreference_action(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
end of function_name2
    """
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parse_tree = parser.parse(input_text)
    assert parse_tree == [
        ['def', 'function_name1', 'end of', 'function_name1'],
        ['def', 'function_name2', 'end of', 'function_name2'],
        '',
    ]


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_single_modifier(klass, grammar_cb, debug, capsys):
    input_text = """
function_name1(1, 2, 3)
"""
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parse_tree = parser.parse(input_text)
    assert parse_tree == [
        ['function_name1', '1', '2', '3'],
        '',
    ]


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_indentation_with_spaces(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
    function_name1(1, 2, 3)
    function_name2(4, 5, 6)

    def inner_function_name
        function_name1(1, 2, 3)
        function_name2(4, 5, 6)
    end of inner_function_name
end of function_name2
"""
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parser.parse(input_text)
