import pytest

# Grammar
from arpeggio import ZeroOrMore, ParserPython, NonTerminal

def grammar():      return first, second
def first():        return ZeroOrMore(["a", "b"], eolterm=True)
def second():       return "a"


def test_eolterm():

    # first rule should match only first line
    # so that second rule will match "a" on the new line
    input = """a a b a b b
    a"""

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(input)

    assert result
