# proj
try:
    # imports for local pytest
    from ....arpeggio import *   # type: ignore # pragma: no cover
except ImportError:              # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import *       # type: ignore # pragma: no cover


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
