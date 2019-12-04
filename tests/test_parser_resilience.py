# stdlib
import pytest  # type: ignore

# proj
from arpeggio import *


def test_parser_resilience():
    """Tests that arpeggio parsers recover successfully from failure."""
    parser = ParserPython(('findme', EOF))
    with pytest.raises(TypeError):
        parser.parse(map)
    assert parser.parse('  findme  ') is not None
