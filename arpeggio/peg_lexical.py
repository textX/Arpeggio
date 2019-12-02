# proj
from . import peg_expressions

# Lexical invariants
LEFT_ARROW = "<-"
ORDERED_CHOICE = "/"
ZERO_OR_MORE = "*"
ONE_OR_MORE = "+"
OPTIONAL = "?"
UNORDERED_GROUP = "#"
AND = "&"
NOT = "!"
OPEN = "("
CLOSE = ")"

# Lexical invariants only used on peg_clean
ASSIGNMENT = "="


def ordered_choice():
    return sequence, peg_expressions.ZeroOrMore(ORDERED_CHOICE, sequence)


def sequence():
    return peg_expressions.OneOrMore(prefix)


def prefix():
    return peg_expressions.Optional([AND, NOT]), sufix


def sufix():
    return expression, peg_expressions.Optional([OPTIONAL,
                                                 ZERO_OR_MORE,
                                                 ONE_OR_MORE,
                                                 UNORDERED_GROUP])


def expression():
    return [regex, rule_crossref,
            (OPEN, ordered_choice, CLOSE),
            str_match]


# PEG Lexical rules
def regex():
    return [("r'", peg_expressions.RegExMatch(r'''[^'\\]*(?:\\.[^'\\]*)*'''), "'"),
            ('r"', peg_expressions.RegExMatch(r'''[^"\\]*(?:\\.[^"\\]*)*'''), '"')]


def rule_name():
    return peg_expressions.RegExMatch(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")


def rule_crossref():
    return rule_name


def str_match():
    """ matches single quoted or double quoted strings """
    return peg_expressions.RegExMatch(r'''(?s)('[^'\\]*(?:\\.[^'\\]*)*')|'''
                                      r'''("[^"\\]*(?:\\.[^"\\]*)*")''')


def comment():
    return "//", peg_expressions.RegExMatch(".*\n")
