try:
    # imports for local pytest
    from .peg_expressions import *                         # type: ignore # pragma: no cover
    from .peg_expressions import RegExMatch as _           # type: ignore # pragma: no cover

except ImportError:                                        # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from peg_expressions import *                          # type: ignore # pragma: no cover
    from peg_expressions import RegExMatch as _            # type: ignore # pragma: no cover

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


def ordered_choice():
    return sequence, ZeroOrMore(ORDERED_CHOICE, sequence)


def sequence():
    return OneOrMore(prefix)


def prefix():
    return Optional([AND, NOT]), sufix


def sufix():
    return expression, Optional([OPTIONAL,
                                 ZERO_OR_MORE,
                                 ONE_OR_MORE,
                                 UNORDERED_GROUP])


def expression():
    return [regex, rule_crossref,
            (OPEN, ordered_choice, CLOSE),
            str_match]


# PEG Lexical rules
def regex():
    return [("r'", _(r'''[^'\\]*(?:\\.[^'\\]*)*'''), "'"),
            ('r"', _(r'''[^"\\]*(?:\\.[^"\\]*)*'''), '"')]


def rule_name():
    return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")


def rule_crossref():
    return rule_name


def str_match():
    return _(r'''(?s)('[^'\\]*(?:\\.[^'\\]*)*')|'''
             r'''("[^"\\]*(?:\\.[^"\\]*)*")''')


def comment():
    return "//", _(".*\n")
