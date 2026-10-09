import pytest  # noqa

# Grammar
from arpeggio import (
    EOF,
    And,
    NoMatch,
    OneOrMore,
    ParserPython,
    RegExMatch,
    StrMatch,
    UnorderedGroup,
    ZeroOrMore,
)


def test_zeroormore_with_separator():
    def grammar():
        return ZeroOrMore(["a", "b"], sep=","), EOF

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse("a, b, b, b, a")
    assert result

    with pytest.raises(NoMatch):
        parser.parse("a, b a")


def test_oneormore_with_ordered_choice_separator():
    def grammar():
        return OneOrMore(["a", "b"], sep=[",", ";"]), EOF

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse("a, a; a,  b, a; a")
    assert result

    with pytest.raises(NoMatch):
        parser.parse("a, b a")

    with pytest.raises(NoMatch):
        parser.parse("a, b: a")


def test_unordered_group_with_separator():
    def grammar():
        return UnorderedGroup("a", "b", "c", sep=[",", ";"]), EOF

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse("b , a, c")
    assert result
    result = parser.parse("b , c; a")
    assert result

    # Check separator matching
    with pytest.raises(NoMatch):
        parser.parse("a, b c")

    with pytest.raises(NoMatch):
        parser.parse("a, c: a")

    # Each element must be matched exactly once
    with pytest.raises(NoMatch):
        parser.parse("a, b, b; c")

    with pytest.raises(NoMatch):
        parser.parse("a, c")


@pytest.mark.parametrize("repetition", [ZeroOrMore, OneOrMore])
@pytest.mark.parametrize("memoization", [False, True])
@pytest.mark.parametrize("lookahead", [False, True])
@pytest.mark.parametrize("text", ["[1,]", "[1,2,]"])
def test_repetition_backtracks_separator(repetition, memoization, lookahead, text):
    def number():
        return RegExMatch(r"\d+")

    def separator():
        return ","

    def values():
        return repetition(number, sep=separator)

    def grammar():
        if lookahead:
            return "[", And(values), values, ",", "]", EOF
        return "[", values, ",", "]", EOF

    parser = ParserPython(grammar, memoization=memoization)
    result = parser.parse(text)
    parsed_values = result.values[0]

    # The comma before ']' belongs only to the enclosing rule. The failed
    # separator/body attempt must leave neither input nor parse tree nodes behind.
    assert result.flat_str() == text
    assert parsed_values.flat_str() == text[1:-2]
    assert parsed_values.position_end == len(text) - 2
    assert parsed_values[-1].rule_name == "number"
    assert result[2].position == parsed_values.position_end
    if memoization and lookahead:
        assert parser.cache_hits > 0


@pytest.mark.parametrize("repetition", [ZeroOrMore, OneOrMore])
@pytest.mark.parametrize("memoization", [False, True])
@pytest.mark.parametrize("separator_kind", ["suppressed", "nullable", "sequence"])
def test_repetition_separator_variants(repetition, memoization, separator_kind):
    def number():
        return RegExMatch(r"\d")

    def separator():
        if separator_kind == "suppressed":
            return StrMatch(",", suppress=True)
        if separator_kind == "nullable":
            return RegExMatch(r",?")
        return ",", ":"

    def values():
        return repetition(number, sep=separator)

    delimiter = ",:" if separator_kind == "sequence" else ","

    def grammar():
        return "[", values, delimiter, "]", EOF

    parser = ParserPython(grammar, memoization=memoization)
    if separator_kind == "sequence":
        text, expected = "[1,:2,:]", "1,:2"
    elif separator_kind == "suppressed":
        text, expected = "[1,2,]", "12"
    else:
        # An empty match between the numbers must remain successful.
        text, expected = "[12,]", "12"
    result = parser.parse(text)
    parsed_values = result.values[0]
    assert parsed_values.flat_str() == expected
    assert parsed_values.position_end == len(text) - len(delimiter) - 1
    assert parsed_values[-1].rule_name == "number"


@pytest.mark.parametrize("repetition", [ZeroOrMore, OneOrMore])
@pytest.mark.parametrize("memoization", [False, True])
def test_repetition_rejects_trailing_separator(repetition, memoization):
    def grammar():
        return repetition("a", sep=","), EOF

    parser = ParserPython(grammar, memoization=memoization)
    with pytest.raises(NoMatch):
        parser.parse("a,")
