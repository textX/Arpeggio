"""
See https://github.com/textX/Arpeggio/issues/43
"""
from arpeggio.cleanpeg import ParserPEG


def try_grammer(peg):
    p = ParserPEG(peg, 'letters', debug=False)
    p.parse(""" { a b } """)
    p.parse(""" { b a } """)


def test_plain_grammar():
    try_grammer("""
    letters = "{" ("a" "b")# "}"
    n = "9"
    """)


def test_bs_at_eol():
    try_grammer("""
    letters = "{" ("a" "b")# "}" \
    n = "9"
    """)


def test_move_unordered_group_to_last_line_in_grammar():
    try_grammer("""
    n = "9"
    letters = "{" ("a" "b")# "}" \
    """)
