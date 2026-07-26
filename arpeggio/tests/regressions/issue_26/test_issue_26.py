import pytest

from arpeggio import GrammarError
from arpeggio.cleanpeg import ParserPEG


def test_regex_with_empty_match_in_repetition_should_fail_validation():
    """Regex that matches empty should fail during grammar construction."""
    grammar = """
            rule = (subexpression)+
            subexpression = r'^.*$'
            """
    with pytest.raises(GrammarError, match="Non-consuming match"):
        ParserPEG(grammar, "rule")
