# stdlib
from typing import Any

# proj
try:
    # imports for local pytest
    from ..arpeggio import ZeroOrMore      # type: ignore # pragma: no cover
    from ..arpeggio import OneOrMore       # type: ignore # pragma: no cover
    from ..arpeggio import ParserPython    # type: ignore # pragma: no cover
    from ..arpeggio import EOF             # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import ZeroOrMore         # type: ignore # pragma: no cover
    from arpeggio import OneOrMore          # type: ignore # pragma: no cover
    from arpeggio import ParserPython       # type: ignore # pragma: no cover
    from arpeggio import EOF                # type: ignore # pragma: no cover


def test_zeroormore_eolterm() -> None:

    def grammar() -> Any:
        return first, second, EOF

    def first() -> Any:
        return ZeroOrMore(["a", "b"], eolterm=True)

    def second() -> Any:
        return "a"

    # first rule should match only first line
    # so that second rule will match "a" on the new line
    input = """a a b a b b
    a"""

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(input)

    assert result


def test_oneormore_eolterm() -> None:

    def grammar() -> Any:
        return first, second, EOF

    def first() -> Any:
        return OneOrMore(["a", "b"], eolterm=True)

    def second() -> Any:
        return "a"

    # first rule should match only first line
    # so that second rule will match "a" on the new line
    input = """a a a  b a
    a"""

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(input)

    assert result
