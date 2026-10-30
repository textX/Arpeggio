import pytest

from arpeggio import EOF, OneOrMore, ParserPython, RegExMatch, ZeroOrMore


@pytest.mark.parametrize("repetition", [ZeroOrMore, OneOrMore])
@pytest.mark.parametrize("memoization", [False, True])
def test_repeated_suppressed_comments_preserve_entries(repetition, memoization):
    class Comment(RegExMatch):
        suppress = True

    def comment():
        return Comment(r"[^@]+")

    def entry():
        return RegExMatch(r"@\w+")

    def grammar():
        return repetition([entry, comment]), EOF

    parser = ParserPython(grammar, memoization=memoization)
    result = parser.parse(
        "leading comment @first middle comment @second trailing comment"
    )

    assert [str(node) for node in result] == ["@first", "@second", ""]
    assert [node.rule_name for node in result] == ["entry", "entry", "EOF"]
