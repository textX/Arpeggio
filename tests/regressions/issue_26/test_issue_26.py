# proj
from arpeggio.parser_peg_clean import ParserPEG


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
