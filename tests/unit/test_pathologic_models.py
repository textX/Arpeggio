import pytest

from arpeggio import ZeroOrMore, Optional, ParserPython, NoMatch


def test_optional_inside_zeroormore():
    def grammar():  return ZeroOrMore(Optional('a'))

    parser = ParserPython(grammar)

    with pytest.raises(NoMatch):
        # This could lead to infinite loop
        parser.parse('b')
