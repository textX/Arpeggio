# stdlib
import pytest                                   # type: ignore
from _pytest.fixtures import FixtureRequest     # type: ignore
import sys
from typing import Any, List, Tuple

# proj
try:
    # imports for local pytest
    from ...arpeggio import ParserPython                    # type: ignore # pragma: no cover
except ImportError:                                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import ParserPython                       # type: ignore # pragma: no cover


def test_memoization_positive(capsys: FixtureRequest) -> None:
    """
    Test that already matched rule is found in the cache on
    subsequent matches.
    Args: capsys - pytest fixture for output capture
    """

    def grammar() -> List[Any]:
        return [(rule1, ruleb), (rule1, rulec)]

    def rule1() -> Tuple[Any, ...]:
        return rulea, ruleb

    def rulea() -> str:
        return "a"

    def ruleb() -> str:
        return "b"

    def rulec() -> str:
        return "c"

    parser = ParserPython(grammar, memoization=True, debug=True)

    # Parse input where a rule1 will match but ruleb will fail
    # Second sequence will try rule1 again on the same location
    # and result should be found in the cache.
    parse_tree = parser.parse("a   b   c")

    # Assert that cached result is used
    assert "Cache hit" in capsys.readouterr()[0]
    assert parser.cache_hits == 1
    assert parser.cache_misses == 4


def test_memoization_nomatch(capsys: FixtureRequest) -> None:
    """
    Test that already failed match is found in the cache on
    subsequent matches.
    """

    def grammar() -> List[Any]:
        return [(rule1, ruleb), [rule1, rulec]]

    def rule1() -> Tuple[Any, ...]:
        return rulea, ruleb

    def rulea() -> str:
        return "a"

    def ruleb() -> str:
        return "b"

    def rulec() -> str:
        return "c"

    parser = ParserPython(grammar, memoization=True, debug=True)
    parse_tree = parser.parse("c")

    assert "Cache hit for [rule1=Sequence, 0] = '0'" in capsys.readouterr()[0]
    assert parser.cache_hits == 1
    assert parser.cache_misses == 4
