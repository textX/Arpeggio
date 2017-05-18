# coding=utf-8

from arpeggio import ParserPython, EOF
import pytest


def test_parser_resilience():
    """Tests that arpeggio parsers recover successfully from failure."""
    parser = ParserPython(('findme', EOF))
    with pytest.raises(TypeError):
        parser.parse(map)
    assert parser.parse('  findme  ') is not None
