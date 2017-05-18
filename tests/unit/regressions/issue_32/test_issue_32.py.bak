# -*- coding: utf-8 -*-

# Test github issue 32: ensure that Python-style escape sequences in peg and
# cleanpeg grammars are properly converted, and ensure that escaping of those
# sequences works as well.

from __future__ import print_function
import re
import sys

import pytest

import arpeggio
from arpeggio.cleanpeg import ParserPEG as ParserCleanPEG
from arpeggio.peg import ParserPEG


def check_parser(grammar, text):
    """Test that the PEG parsers correctly parse a grammar and match the given
    text. Test both the peg and cleanpeg parsers. Raise an exception if the
    grammar parse failed, and returns False if the match fails. Otherwise,
    return True.

    Parameters:
    grammar -- Not the full grammar, but just the PEG expression for a string
               literal or regex match, e.g. "'x'" to match an x.
    text    -- The text to test against the grammar for a match.
    """
    # test the peg parser
    parser = ParserPEG('top <- ' + grammar + ' EOF;', 'top', skipws=False)
    if parser.parse(text) is None:
        return False

    # test the cleanpeg parser
    parser = ParserCleanPEG('top = ' + grammar + ' EOF', 'top', skipws=False)
    if parser.parse(text) is None:
        return False

    return True


def check_regex(grammar, text):
    """Before calling check_parser(), verify that the regular expression
    given in ``grammar`` matches ``text``. Only works for single regexs.
    """
    if not re.match(eval(grammar).strip() + '$', text):
        return False
    return check_parser(grammar, text)


# ==== Make sure things are working as expected. ====

def test_harness():
    assert check_parser(r"'x'", 'x')
    with pytest.raises(arpeggio.NoMatch):
        check_parser(r"'x'", 'y')
    with pytest.raises(arpeggio.NoMatch):
        check_parser(r"'x'", 'xx')
    assert check_parser(r"'x' 'y'", 'xy')
    assert check_parser(r"'\''", "'")
    assert check_regex(r"r'x'", 'x')


# ==== Check things that were broken in arpeggio 1.5 @ commit 25dae48 ====

# ---- string literal quoting ----

def test_literal_quoting_1():
    # this happens to work in 25dae48 if there are no subsequent single quotes
    # in the grammar:
    assert check_parser(r"'\\'", '\\')
    # add subsequent single quotes and it fails:
    assert check_parser(r"""  '\\' 'x'  """, '\\x')


def test_literal_quoting_2():
    # this grammar should fail to parse, but passes on 25dae48:
    with pytest.raises(arpeggio.NoMatch):
        check_parser(r"""  '\\'x'  """, r"\'x")


def test_literal_quoting_3():
    # escaping double quotes within double-quoted strings was not implemented
    # in 25dae48:
    assert check_parser(r'''  "x\"y"  ''', 'x"y')


# ---- now repeat the above section with single and double quotes swapped ----

def test_literal_quoting_4():
    assert check_parser(r'"\\"', '\\')
    assert check_parser(r'''  "\\" "x"  ''', '\\x')


def test_literal_quoting_5():
    with pytest.raises(arpeggio.NoMatch):
        check_parser(r'''  "\\"x"  ''', r'\"x')


def test_literal_quoting_6():
    assert check_parser(r"""  'x\'y'  """, "x'y")


# ---- regular expression quoting ----

# Because arpeggio has treated regular expressions in PEG grammars most
# nearly like raw strings, the tests below expect the peg and cleanpeg
# grammars to behave such that "rule <- r'<sometext>';" will match the
# same text as the Python expression "re.match(r'<sometext>')".
#
# This can be a little surprising at times, since Python's handling of
# quotes inside raw strings is somewhat odd. Raw strings "treat backslashes
# as literal characters"[1], yet a backslash also functions as an escape
# character before certain characters:
#   - before quotes inside a string (e.g. "r'x\'x'" is accepted as the
#       string "x\'x"),
#   - before another backslash (e.g. "r'x\\'x'" fails with a syntax error,
#       while "r'x\\x' is accepted as the string "x\\x"), and
#   - similarly before a newline.
#
# [1] https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals

def test_regex_quoting_1():
    assert check_regex(r"r'\\'", '\\')
    assert check_regex(r'r"\\"', '\\')
    assert check_parser(r"""  r'\\' r'x'  """, '\\x')
    assert check_parser(r'''  r"\\" r"x"  ''', '\\x')


def test_regex_quoting_2():
    with pytest.raises(arpeggio.NoMatch):
        check_parser(r"""  r'\\' '  """, "\\' ")
    with pytest.raises(arpeggio.NoMatch):
        check_parser(r'''  r"\\" "  ''', '\\" ')


def test_regex_quoting_3():
    assert check_regex(r"""  r'x\'y'  """, "x'y")
    assert check_regex(r'''  r"x\"y"  ''', 'x"y')


# ---- string literal escape sequence translation ----

def test_broken_escape_translation():
    # 25dae48 would translate this as 'newline-newline', not 'backslash-n-newline'.
    assert check_parser(r"'\\n\n'", '\\n\n')
    assert check_parser(r"'\\t\t'", '\\t\t')


def test_multiple_backslash_sequences():
    assert check_parser(r"'\\n'",    '\\n')    # backslash-n
    assert check_parser(r"'\\\n'",   '\\\n')   # backslash-newline
    assert check_parser(r"'\\\\n'",  '\\\\n')  # backslash-backslash-n
    assert check_parser(r"'\\\\\n'", '\\\\\n') # backslash-backslash-newline


# ==== Check newly-implemented escape sequences ====

def test_single_character_escapes():
    # make sure parsing across newlines works, otherwise the following
    # backslash-newline test won't work:
    assert check_parser(" \n 'x' \n ", 'x')
    # a compact test is clearer for failure diagnosis:
    assert check_parser("'x\\\ny'", 'xy')  # backslash-newline
    # but this would probably only be used like so:
    assert check_parser("""  'extremely_\
long_\
match'  """, 'extremely_long_match')

    # the remaining single-character escapes:
    assert check_parser(r'"\\"', '\\')     # \\
    assert check_parser(r"'\''", "'")      # \'
    assert check_parser("'\\\"'", '"')     # \"
    assert check_parser(r"'\a'", '\a')
    assert check_parser(r"'\b'", '\b')
    assert check_parser(r"'\f'", '\f')
    assert check_parser(r"'\n'", '\n')
    assert check_parser(r"'\r'", '\r')
    assert check_parser(r"'\t'", '\t')
    assert check_parser(r"'\v'", '\v')

    # unrecognized escape sequences *are not changed*
    assert check_parser(r"'\x'", '\\x')


def test_octal_escapes():
    assert check_parser(r"'\7'",    '\7')
    assert check_parser(r"'\41'",   '!')
    assert check_parser(r"'\101'",  'A')
    assert check_parser(r"'\1001'", '@1')  # too long


def test_hexadecimal_escapes():
    assert check_parser(r"'\x41'",  'A')
    assert check_parser(r"'\x4A'",  'J')
    assert check_parser(r"'\x4a'",  'J')
    assert check_parser(r"'\x__'",  '\\x__')  # too short
    assert check_parser(r"'\x1_'",  '\\x1_')  # too short
    assert check_parser(r"'\x411'", 'A1')     # too long


def test_small_u_unicode_escapes():
    assert check_parser(r"'\u0041'", 'A')
    assert check_parser(r"'\u004A'", 'J')
    assert check_parser(r"'\u004a'", 'J')
    assert check_parser(r"'\u____'", '\\u____')  # too short
    assert check_parser(r"'\u1___'", '\\u1___')  # too short
    assert check_parser(r"'\u41__'", '\\u41__')  # too short
    assert check_parser(r"'\u041_'", '\\u041_')  # too short
    assert check_parser(r"'\u00411'", 'A1')      # too long


def test_big_u_unicode_escapes():
    assert check_parser(r"'\U00000041'", 'A')
    assert check_parser(r"'\U0000004A'", 'J')
    assert check_parser(r"'\U0000004a'", 'J')
    assert check_parser(r"'\U________'", '\\U________')  # too short
    assert check_parser(r"'\U1_______'", '\\U1_______')  # too short
    assert check_parser(r"'\U41______'", '\\U41______')  # too short
    assert check_parser(r"'\U041_____'", '\\U041_____')  # too short
    assert check_parser(r"'\U0041____'", '\\U0041____')  # too short
    assert check_parser(r"'\U00041___'", '\\U00041___')  # too short
    assert check_parser(r"'\U000041__'", '\\U000041__')  # too short
    assert check_parser(r"'\U0000041_'", '\\U0000041_')  # too short
    assert check_parser(r"'\U000000411'", 'A1')          # too long
    with pytest.raises(arpeggio.GrammarError):
        check_parser(r"'\U00110000'", '?')  # out-of-range


def test_unicode_name_escapes():
    assert check_parser(r"'\N{LATIN SMALL LETTER B}'", 'b')

    if sys.version_info >= (3, 3):
        # check that Unicode name aliases work as well
        assert check_parser(r"'\N{LATIN CAPITAL LETTER GHA}'", '\u01a2')

    with pytest.raises(arpeggio.GrammarError):
        check_parser(r"'\N{NOT A VALID NAME}'", '\\N{NOT A VALID NAME}')

    # This shouldn't raise, because it shouldn't pass the valid-escape filter:
    assert check_parser(r"'\N{should not match filter regex!}'",
                        '\\N{should not match filter regex!}')
