"""
See https://github.com/textX/Arpeggio/issues/43
"""

# proj
try:
    # imports for local pytest
    from ....cleanpeg import ParserPEG      # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from cleanpeg import ParserPEG          # type: ignore # pragma: no cover


def try_grammar(peg: str) -> None:
    p = ParserPEG(peg, 'letters', debug=False)
    p.parse(""" { a b } """)
    p.parse(""" { b a } """)


def test_plain_grammar() -> None:
    try_grammar("""
    letters = "{" ("a" "b")# "}"
    n = "9"
    """)


def test_bs_at_eol() -> None:
    try_grammar("""
    letters = "{" ("a" "b")# "}" \
    n = "9"
    """)


def test_move_unordered_group_to_last_line_in_grammar() -> None:
    try_grammar("""
    n = "9"
    letters = "{" ("a" "b")# "}" \
    """)
