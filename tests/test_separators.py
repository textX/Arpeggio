import pytest  # type: ignore


# proj
from arpeggio import *


def test_zero_or_more_with_separator():

    def grammar():
        return ZeroOrMore(['a', 'b'], sep=','), EOF

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse('a, b, b, b, a')
    assert result

    with pytest.raises(NoMatch):
        parser.parse('a, b a')


def test_one_or_more_with_ordered_choice_separator():

    def grammar():
        return OneOrMore(['a', 'b'], sep=[',', ';']), EOF

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse('a, a; a,  b, a; a')
    assert result

    with pytest.raises(NoMatch):
        parser.parse('a, b a')

    with pytest.raises(NoMatch):
        parser.parse('a, b: a')


def test_unordered_group_with_separator():

    def grammar():
        return UnorderedGroup('a', 'b', 'c', sep=[',', ';']), EOF

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse('b , a, c')
    assert result
    result = parser.parse('b , c; a')
    assert result

    # Check separator matching
    with pytest.raises(NoMatch):
        parser.parse('a, b c')

    with pytest.raises(NoMatch):
        parser.parse('a, c: a')

    # Each element must be matched exactly once
    with pytest.raises(NoMatch):
        parser.parse('a, b, b; c')

    with pytest.raises(NoMatch):
        parser.parse('a, c')
