# stdlib
import pytest  # type: ignore

# proj
try:
    # imports for local pytest
    from ..arpeggio import *                                # type: ignore # pragma: no cover
    from ..arpeggio import RegExMatch as _                  # type: ignore # pragma: no cover
except ImportError:                                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import *                                  # type: ignore # pragma: no cover
    from arpeggio import RegExMatch as _                    # type: ignore # pragma: no cover


def test_parser_resilience():
    """Tests that arpeggio parsers recover successfully from failure."""
    parser = ParserPython(('findme', EOF))
    with pytest.raises(TypeError):
        parser.parse(map)
    assert parser.parse('  findme  ') is not None
