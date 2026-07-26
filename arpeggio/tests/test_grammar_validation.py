"""Tests for grammar validation (detecting non-consuming matches in repetitions)."""

import pytest

from arpeggio import (
    EOF,
    And,
    Empty,
    GrammarError,
    NoMatch,
    Not,
    OneOrMore,
    Optional,
    ParserPython,
    RegExMatch,
    StrMatch,
    UnorderedGroup,
    ZeroOrMore,
)


# --- Helper: construct and parse a grammar, expecting success ---
def _parse(grammar_def, input_str="x"):
    parser = ParserPython(grammar_def)
    return parser.parse(input_str)


# --- Cases that should raise GrammarError ---


def test_zero_or_more_with_empty_regex():
    """ZeroOrMore containing a regex that matches empty should fail."""

    def grammar():
        return ZeroOrMore(RegExMatch(r".*")), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_one_or_more_with_optional():
    """OneOrMore containing Optional should fail."""

    def grammar():
        return OneOrMore(Optional("x")), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_zero_or_more_with_zero_or_more():
    """ZeroOrMore containing another ZeroOrMore should fail."""

    def grammar():
        return ZeroOrMore(ZeroOrMore("x")), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_zero_or_more_with_not():
    """ZeroOrMore containing Not should fail (syntax predicates don't consume)."""

    def grammar():
        return ZeroOrMore(Not("y")), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_zero_or_more_with_and():
    """ZeroOrMore containing And should fail."""

    def grammar():
        return ZeroOrMore(And("y")), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_zero_or_more_with_empty():
    """ZeroOrMore containing Empty should fail."""

    def grammar():
        return ZeroOrMore(Empty()), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_one_or_more_with_empty_strmatch():
    """OneOrMore containing empty StrMatch should fail."""

    def grammar():
        return OneOrMore(StrMatch("")), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_zero_or_more_with_non_consuming_sequence():
    """ZeroOrMore containing a Sequence where all parts are non-consuming."""

    def grammar():
        return ZeroOrMore((Optional("x"), Optional("y"))), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_zero_or_more_with_non_consuming_ordered_choice():
    """ZeroOrMore containing OrderedChoice with a non-consuming alternative."""

    def grammar():
        return ZeroOrMore(["x", Optional("x")]), EOF

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


def test_non_consuming_through_rule_indirection():
    """Non-consuming match detected through rule reference resolution."""

    def grammar():
        return ZeroOrMore(sub), EOF

    def sub():
        return RegExMatch(r".*")

    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPython(grammar)


# --- Cases that should NOT raise GrammarError ---


def test_zero_or_more_with_literal():
    """ZeroOrMore containing a normal string match should pass."""
    _parse(lambda: (ZeroOrMore("x"), EOF))


def test_one_or_more_with_regex_that_requires_input():
    """OneOrMore with a regex that always consumes at least one character."""
    _parse(lambda: (OneOrMore(RegExMatch(r"\w+")), EOF))


def test_zero_or_more_with_sequence_that_consumes():
    """Sequence where at least one child consumes input should pass."""
    _parse(lambda: (ZeroOrMore(("x", Optional("y"))), EOF), "xy x xyx")


def test_optional_not_directly_in_repetition():
    """Optional at the top level is fine."""
    _parse(lambda: (Optional("x"), "y", EOF), "y")


def test_syntax_predicate_not_directly_in_repetition():
    """Not/And at the top level is fine."""
    _parse(lambda: (Not("y"), RegExMatch(r"\w+"), EOF), "hello")


def test_unordered_group_in_repetition_with_consuming_children():
    """UnorderedGroup that consumes input is fine."""

    def grammar():
        return ZeroOrMore(UnorderedGroup(["a", "b"])), EOF

    _parse(grammar, "ab ba")


def test_one_or_more_with_ordered_choice_all_consuming():
    """OrderedChoice where all alternatives consume is fine."""

    def grammar():
        return OneOrMore(["x", "yz"]), EOF

    _parse(grammar, "x yz x")


def test_and_not_inside_unordered_group():
    """Not outside repetition is fine."""

    def grammar():
        return ("x", Not("y"), RegExMatch(r"\w+")), EOF

    _parse(grammar, "x z")
    # "x y" should fail: Not("y") rejects
    with pytest.raises(NoMatch):
        _parse(grammar, "x y")


# --- PEG syntax validation ---


def test_peg_syntax_grammar_does_not_fail_validation():
    """The PEG parser's own grammar should pass validation."""
    from arpeggio.peg import ParserPEG

    grammar = 'root <- first second; first <- "hello"; second <- "world";'
    parser = ParserPEG(grammar, "root")
    assert parser


def test_cleanpeg_syntax_grammar_does_not_fail_validation():
    """The clean PEG parser's own grammar should pass validation."""
    from arpeggio.cleanpeg import ParserPEG

    grammar = """
    root = first second
    first = 'hello'
    second = 'world'
    """
    parser = ParserPEG(grammar, "root")
    assert parser


def test_peg_grammar_with_non_consuming_repetition():
    """PEG grammar with non-consuming repetition should fail validation."""
    from arpeggio.peg import ParserPEG

    grammar = "root <- (empty_regex)*; empty_regex <- r'.*';"
    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPEG(grammar, "root")


def test_cleanpeg_grammar_with_non_consuming_repetition():
    """Clean PEG grammar with non-consuming repetition should fail validation."""
    from arpeggio.cleanpeg import ParserPEG

    grammar = """
    root = empty_regex*
    empty_regex = r'.*'
    """
    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPEG(grammar, "root")
