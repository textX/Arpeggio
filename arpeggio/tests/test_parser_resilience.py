import pytest

from arpeggio import EOF, ParserPython


def test_parser_resilience():
    """Tests that arpeggio parsers recover successfully from failure."""
    parser = ParserPython(('findme', EOF))
    with pytest.raises(TypeError):
        parser.parse(map)
    assert parser.parse('  findme  ') is not None
