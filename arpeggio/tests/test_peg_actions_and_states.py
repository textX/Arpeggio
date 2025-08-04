#######################################################################
# Name: test_peg_actions_and_states
# Purpose: Test for parser constructed using PEG textual grammars using the actions and states system.
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
    / function_with_suppressed_keywords
    / global_function
    / function_call
    / erroneous_non_closed_start
    / erroneous_non_closed_end;

function <-
    @(
        FUNCTION_START function_name{push, parent add}
            program_element*
        // Test And expression not changing the state of the parser
        // Also, test quoted argument
        FUNCTION_END &function_name{'pop'} function_name{pop}
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

function_with_suppressed_keywords <-
    @(
        FUNCTION_START_SUPPRESSED function_name{push, parent add}
            program_element*
        FUNCTION_END_SUPPRESSED function_name{pop, 'suppress'}
    );

function_call <-
    function_name{any}
    ARGUMENTS_START
    (
        VALID_NAME
        % ARGUMENTS_DELIMITER
    )*
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

erroneous_non_closed_start <-
    ERRONEOUS FUNCTION_START function_name{push, add};

erroneous_non_closed_end <-
    ERRONEOUS FUNCTION_END function_name{pop};

FUNCTION_START_SUPPRESSED <- 'suppressed def'{suppress};
FUNCTION_END_SUPPRESSED <- 'suppressed end of'{suppress};

FUNCTION_START <- 'def';
function_name <- VALID_NAME;
FUNCTION_END <- 'end of';
ARGUMENTS_START <- '(';
ARGUMENTS_END <- ')';
VALID_NAME <- r'[a-zA-Z0-9_]+';
ARGUMENTS_DELIMITER <- ',';
DEFER <- r'defer(?=\s)';
DEFER_DELIMITER <- ':';
ANONYMOUS_DEFER <- 'anonymous defer';
DEFERRED <- 'deferred';
END <- 'end';
GLOBAL <- r'global(?=\s)';
ERRONEOUS <- 'erroneous';
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
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_non_popped(klass, grammar_cb, debug, capsys):
    input_text = """
erroneous def function_name1
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.GrammarError):
        parser.parse(input_text)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_non_popped_in_state_layer(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name0
    erroneous def function_name1
end of function_name0
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.GrammarError) as e:
        parser.parse(input_text)
    assert 'in the state layer' in e.value.message


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_non_pushed(klass, grammar_cb, debug, capsys):
    input_text = """
erroneous end of function_name1
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.NoMatch):
        parser.parse(input_text)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
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
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parse_tree = parser.parse(input_text)
    assert parse_tree == [
        ["def", "function_name1", "end of", "function_name1"],
        ["def", "function_name2", ["function_name1", "(", "arg1", ")"], "end of", "function_name2"],
        ["function_name1", "(", "1", ",", "2", ",", "3", ")"],
        ["function_name2", "(", "1", ",", "2", ",", "3", ")"],
        ""  # EOF
    ]

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
def test_backreference_any_not_met(klass, grammar_cb, debug, capsys):
    input_text = """
function_name1(arg1)
"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.NoMatch):
        parser.parse(input_text)


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
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parse_tree = parser.parse(input_text)
    assert parse_tree == [
        ["def", "function_name1", "end of", "function_name1"],
        ["def", "function_name2", "end of", "function_name2"],
        [
            "def", "function_name3",
            ["defer", "function_name1"],
            ["defer", "function_name2"],
            ["function_name1", ":"],
            ["function_name1", "(", "1", ",", "2", ",", "3", ")"],
            ["function_name2", ":"],
            ["function_name2", "(", "1", ",", "2", ",", "3", ")"],
            "end of", "function_name3"
         ],
        ""
    ]

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
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parse_tree = parser.parse(input_text)
    assert parse_tree == [
        ["def", "function_name1", "end of", "function_name1"],
        ["def", "function_name2", "end of", "function_name2"],
        [
            "def", "function_name3",
            "anonymous defer",
            "anonymous defer",
            ["deferred", ["function_name1", "(", "1", ",", "2", ",", "3", ")"], "end"],
            ["deferred", ["function_name2", "(", "1", ",", "2", ",", "3", ")"], "end"],
            "end of", "function_name3"
        ],
        ""
    ]

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
def test_backreference_with_wrong_state(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

deferred
    function_name1(1, 2, 3)
end
"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.NoMatch):
        parser.parse(input_text)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_with_wrong_state_in_state_layer(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
end of function_name1

def function_name2
    deferred
        function_name1(1, 2, 3)
    end
end of function_name2
"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.NoMatch):
        parser.parse(input_text)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_with_not_popped_state_within_state_layer(klass, grammar_cb, debug, capsys):
    input_text = """
def function_name1
    anonymous defer
end of function_name1
"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.GrammarError):
        parser.parse(input_text)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_backreference_with_not_popped_state_within_global_state_layer(klass, grammar_cb, debug, capsys):
    input_text = """
anonymous defer
"""
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)
    with pytest.raises(arpeggio.GrammarError):
        parser.parse(input_text)


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


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_state_reentrance(klass, grammar_cb, debug, capsys):
    input_text1 = """
erroneous def function_name1
    """
    parser: ParserPEG = klass(grammar_cb(), 'parser_entry', debug=debug)

    with pytest.raises(arpeggio.GrammarError):
        parser.parse(input_text1)

    input_text2 = """
erroneous end of function_name1
    """
    with pytest.raises(arpeggio.NoMatch):
        # If parser.state is not cleared then this rule will pass, but the state should be cleared on every parse.
        parser.parse(input_text2)


@pytest.mark.parametrize('klass, grammar_cb, debug', [
    (ParserPEGClean, get_clean_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.DISABLED),
    (ParserPEG, get_grammar, Debugging.ENABLED),
])
def test_suppress_action(klass, grammar_cb, debug, capsys):
    input_text = """
suppressed def function_name1
suppressed end of function_name1

suppressed def function_name2
    function_name1(arg1)
suppressed end of function_name2

function_name1(1, 2, 3)
function_name2(1, 2, 3)
"""
    parser: ParserPEG = klass(
        grammar_cb(),
        'parser_entry',
        debug = debug,  # noqa: E251
        reduce_tree = True,  # noqa: E251
    )
    parse_tree = parser.parse(input_text)
    assert parse_tree == [
        "function_name1",
        ["function_name2", ["function_name1", "(", "arg1", ")"]],
        ["function_name1", "(", "1", ",", "2", ",", "3", ")"],
        ["function_name2", "(", "1", ",", "2", ",", "3", ")"],
        ""  # EOF
    ]

    with pytest.raises(Exception) as e:
        parser.state.pop_rule_reference('function_name')
    assert e is not None

    if parser.debug:
        output = capsys.readouterr()
        assert 'states stack' in output.out
