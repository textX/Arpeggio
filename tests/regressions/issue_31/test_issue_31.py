# proj
from arpeggio import *   # type: ignore # pragma: no cover


def test_empty_nested_parse() -> None:

    def grammar():
        return [first]

    def first():
        return ZeroOrMore("second")

    parser = ParserPython(grammar)

    # Parse tree will be empty
    # as nothing will be parsed
    tree = parser.parse("something")

    assert not tree
