# proj

try:
    # for pytest
    from ....cleanpeg import ParserPEG      # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # for local Doctest
    from cleanpeg import ParserPEG          # type: ignore # pragma: no cover


def test_regex_with_empty_successful_match_in_repetition() -> None:
    grammar = \
        """
        rule = (subexpression)+
        subexpression = r'^.*$'
        """
    parser = ParserPEG(grammar, "rule")
    parsed = parser.parse("something simple")

    assert parsed.rule_name == "rule"
    assert parsed.subexpression.rule_name == "subexpression"
