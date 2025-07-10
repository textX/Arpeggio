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

import arpeggio
from arpeggio.peg import ParserPEG
from arpeggio.cleanpeg import ParserPEG as ParserPEGClean
import enum


# Functions are used instead of variables to store grammar only to make parametrized test results readable
def get_grammar():
    return r'''
parser_entry <- program_element* EOF;

program_element <-
    anonymous_defer
    / anonymous_deferred
    / defer_call
    / defer
    / function
    / alternative_function
    / global_function
    / function_call;

function <-
    @(
        FUNCTION_START function_name{push, parent add}
            program_element*
        // Test And expression not changing the state of the parser
        FUNCTION_END &function_name{pop} function_name{pop}
    );

global_function <-
    GLOBAL
    @(
        FUNCTION_START function_name{push, global add}
            program_element*
        // Test And expression not changing the state of the parser
        FUNCTION_END &function_name{pop} function_name{pop}
    );

alternative_function <-
    // Test branching with push action
    FUNCTION_START function_name{push, add}
    @(
        program_element*
        // `*` operator is greedy so the closing `)` won't be matched until all the program_element statements are found
    )
    '/' function_name{pop};

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

defer_call <-
    DEFER defer_name{push};

defer <-
    defer_name{pop_front} DEFER_DELIMITER;

defer_name <- VALID_NAME;

anonymous_defer <-
    ANONYMOUS_DEFER +@anonymous_defer;

anonymous_deferred <-
    @anonymous_defer DEFERRED
    program_element*
    END -@anonymous_defer;

FUNCTION_START <- 'def';
function_name <- VALID_NAME;
FUNCTION_END <- 'end of';
ARGUMENTS_START <- '(';
ARGUMENTS_END <- ')';
VALID_NAME <- r'[a-zA-Z0-9_]+';
ARGUMENTS_DELIMITER <- ',';
DEFER <- 'defer';
DEFER_DELIMITER <- ':';
ANONYMOUS_DEFER <- 'anonymous defer';
DEFERRED <- 'deferred';
END <- 'end';
GLOBAL <- r'global(?=\s)';
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
def test_backreference(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
end of function_name2
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    function_names = parser.state.known_rule_references('function_name')
    assert isinstance(function_names, set)
    assert len(function_names) == 2

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, True),
])
def test_backreference_any(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
    function_name1(arg1)
end of function_name2

function_name1(1, 2, 3)
function_name2(1, 2, 3)
"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_pop_front(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
end of function_name2

def function_name3
    defer function_name1
    defer function_name2

    function_name1:
        function_name1(1, 2, 3)
    function_name2:
        function_name2(1, 2, 3)
end of function_name3

"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_with_state(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
end of function_name2

def function_name3
    anonymous defer
    anonymous defer

    deferred
        function_name1(1, 2, 3)
    end

    deferred
        function_name2(1, 2, 3)
    end
end of function_name3

"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None
    assert parser.state.parsing_state is None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_with_lookahead(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
/function_name1

def function_name2
end of function_name2
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    function_names = parser.state.known_rule_references('function_name')
    assert isinstance(function_names, set)
    assert len(function_names) == 2

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_not_found(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name2
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.NoMatch):
        parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_any_not_found(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
    not_found(1, 2, 3)
end of function_name1
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.NoMatch):
        parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_global_add(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
    global def global_function_name
    end of global_function_name
end of function_name1

global_function_name(1, 2, 3)
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_wrapping_with_state_layer(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
    def local_function_name
    end of local_function_name
end of function_name1

local_function_name(1, 2, 3)
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.NoMatch):
        parser.parse(input_text)

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out
