from __future__ import unicode_literals
import pytest  # noqa

# Grammar
from arpeggio import ZeroOrMore, OneOrMore, ParserPython, EOF


def test_zeroormore_eolterm():

    def grammar():      return first, second, EOF
    def first():        return ZeroOrMore(["a", "b"], eolterm=True)
    def second():       return "a"

    # first rule should match only first line
    # so that second rule will match "a" on the new line
    input = """a a b a b b
    a"""

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(input)

    assert result


def test_oneormore_eolterm():

    def grammar():      return first, second, EOF
    def first():        return OneOrMore(["a", "b"], eolterm=True)
    def second():       return "a"

    # first rule should match only first line
    # so that second rule will match "a" on the new line
    input = """a a a  b a
    a"""

    parser = ParserPython(grammar, reduce_tree=False)
    result = parser.parse(input)

    assert result
