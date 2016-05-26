from __future__ import unicode_literals
import pytest
import sys
from arpeggio import ParserPython


def test_memoization_positive(capsys):
    '''
    Test that already matched rule is found in the cache on
    subsequent matches.
    Args:
        capsys - pytest fixture for output capture
    '''

    def grammar():  return [(rule1, ruleb), (rule1, rulec)]
    def rule1():    return rulea, ruleb
    def rulea():    return "a"
    def ruleb():    return "b"
    def rulec():    return "c"

    parser = ParserPython(grammar, memoization=True, debug=True)

    # Parse input where a rule1 will match but ruleb will fail
    # Second sequence will try rule1 again on the same location
    # and result should be found in the cache.
    parse_tree = parser.parse("a   b   c")

    # Assert that cached result is used
    assert  "Cache hit" in capsys.readouterr()[0]
    assert parser.cache_hits == 1
    assert parser.cache_misses == 4

def test_memoization_nomatch(capsys):
    '''
    Test that already failed match is found in the cache on
    subsequent matches.
    '''

    def grammar():  return [(rule1, ruleb), [rule1, rulec]]
    def rule1():    return rulea, ruleb
    def rulea():    return "a"
    def ruleb():    return "b"
    def rulec():    return "c"

    parser = ParserPython(grammar, memoization=True, debug=True)
    parse_tree = parser.parse("c")

    assert  "Cache hit for [rule1=Sequence, 0] = '0'" in capsys.readouterr()[0]
    assert parser.cache_hits == 1
    assert parser.cache_misses == 4


