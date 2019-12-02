# stdlib
from typing import Any

# proj
from arpeggio import *


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
