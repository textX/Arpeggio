# stdlib
import pytest   # type: ignore

# proj
try:
    # imports for local pytest
    from ....arpeggio import ParserPython   # type: ignore # pragma: no cover
    from ....arpeggio import ZeroOrMore     # type: ignore # pragma: no cover
    from ....arpeggio import Sequence       # type: ignore # pragma: no cover
    from ....arpeggio import OrderedChoice  # type: ignore # pragma: no cover
    from ....arpeggio import EOF            # type: ignore # pragma: no cover
    from ....arpeggio import NoMatch        # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import ParserPython       # type: ignore # pragma: no cover
    from arpeggio import ZeroOrMore         # type: ignore # pragma: no cover
    from arpeggio import Sequence           # type: ignore # pragma: no cover
    from arpeggio import OrderedChoice      # type: ignore # pragma: no cover
    from arpeggio import EOF                # type: ignore # pragma: no cover
    from arpeggio import NoMatch            # type: ignore # pragma: no cover


def test_ordered_choice_skipws_ws() -> None:

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
    def sentence2():
        return Sequence(ZeroOrMore(word2), skipws=True), EOF

    def word2():
        return OrderedChoice([(id, ' ', '.'), id, '.'], skipws=False)

    parser = ParserPython(sentence2)

    with pytest.raises(NoMatch):
        # This can't parse anymore
        parser.parse("id id .")

    tree = parser.parse("idid.")
    assert len(tree) == 4
    # This is the case where 'id .' will be matched by the first alternative of
    # word as there is no ws skipping
    tree = parser.parse("idid .")
    assert len(tree) == 3
