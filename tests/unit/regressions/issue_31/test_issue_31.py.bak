from __future__ import unicode_literals
from arpeggio import ParserPython, ZeroOrMore


def test_empty_nested_parse():

    def grammar(): return [first]
    def first(): return ZeroOrMore("second")

    parser = ParserPython(grammar)

    # Parse tree will be empty
    # as nothing will be parsed
    tree = parser.parse("something")

    assert not tree

