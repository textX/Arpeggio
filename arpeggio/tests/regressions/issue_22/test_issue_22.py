import os
from arpeggio.cleanpeg import ParserPEG


def test_issue_22():
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
