# stdlib
import os

# proj
try:
    # imports for local pytest
    from ....parser_peg_clean import ParserPEG      # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from parser_peg_clean import ParserPEG          # type: ignore # pragma: no cover


def test_issue_22() -> None:
    """
    Infinite recursion during resolving of a grammar given in a clean PEG
    notation.
    """
    current_dir = os.path.dirname(__file__)

    grammar1 = open(os.path.join(current_dir, 'grammar1.peg')).read()
    parser1 = ParserPEG(grammar1, 'belang')
    parser1.parse('a [0]')
    parser1.parse('a (0)')

    grammar2 = open(os.path.join(current_dir, 'grammar2.peg')).read()
    parser2 = ParserPEG(grammar2, 'belang', debug=True)
    parser2.parse('a [0](1)[2]')
