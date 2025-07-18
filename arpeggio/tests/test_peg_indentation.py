#######################################################################
# Name: test_peg_indentation
# Purpose: Test actions that can be used to parse indentation.
# Authors: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@yandex.ru>
# Copyright: (c) 2025
#           Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>,
#           Andrey N. Dotsenko <pgandrey@yandex.ru>
# License: MIT License
#
# This file is originally based on test_peg_actions_and_states.py
#######################################################################

import pytest

from arpeggio import NoMatch
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
    function_with_underscores
    / function_call;

function_with_underscores <-
    @(
        FUNCTION_START function_name{push, parent add}
        (
            INDENTATION{parent list longer, list append, suppress} program_element
            (INDENTATION{list last, suppress} program_element)*
        )?
        INDENTATION{parent list last, list try remove, suppress} FUNCTION_END function_name{pop}
    );


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
INDENTATION <- r'_*';
'''


def get_clean_grammar():
    return get_grammar().replace('<-', '=').replace(';', '')


class Debugging(enum.Flag):
    ENABLED = True
    DISABLED = False


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, True),
])
def test_parent_last_last_longer(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
____function_name1(1, 2, 3)
____function_name2(4, 5, 6)
____def inner_function_name
________function_name1(1, 2, 3)
________function_name2(4, 5, 6)
____end of inner_function_name
end of function_name2
"""
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parser.parse(input_text)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, True),
])
def test_wrong_indentation(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
____function_name1(1, 2, 3)
____function_name2(4, 5, 6)

____def inner_function_name
____function_name1(1, 2, 3)
____function_name2(4, 5, 6)
____end of inner_function_name
end of function_name2

"""
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    with pytest.raises(NoMatch):
        parser.parse(input_text)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, True),
])
def test_wrong_indentation_at_end(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
____function_name1(1, 2, 3)
____function_name2(4, 5, 6)

____def inner_function_name
______function_name1(1, 2, 3)
______function_name2(4, 5, 6)
___end of inner_function_name
end of function_name2

"""
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    with pytest.raises(NoMatch):
        parser.parse(input_text)
