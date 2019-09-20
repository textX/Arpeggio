from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, ZeroOrMore, Sequence, OrderedChoice, \
    EOF, NoMatch


def test_ordered_choice_skipws_ws():

    # Both rules will skip white-spaces
    def sentence():
        return Sequence(ZeroOrMore(word), skipws=True), EOF

    def word():
        return OrderedChoice([(id, ' ', '.'), id, '.'], skipws=True)

    def id():
        return 'id'

    parser = ParserPython(sentence)

    # Thus this parses without problem
    # But the length is always 3 + EOF == 4
    # First alternative of word rule never matches
    tree = parser.parse("id id .")
    assert len(tree) == 4
    tree = parser.parse("id id.")
    assert len(tree) == 4
    tree = parser.parse("idid.")
    assert len(tree) == 4
    tree = parser.parse("idid .")
    assert len(tree) == 4

    # Now we change skipws flag
    def word():  # noqa
        return OrderedChoice([(id, ' ', '.'), id, '.'], skipws=False)

    parser = ParserPython(sentence)

    with pytest.raises(NoMatch):
        # This can't parse anymore
        parser.parse("id id .")

    tree = parser.parse("idid.")
    assert len(tree) == 4
    # This is the case where 'id .' will be matched by the first alternative of
    # word as there is no ws skipping
    tree = parser.parse("idid .")
    assert len(tree) == 3
