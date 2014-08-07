#######################################################################
# Name: textx.py
# Purpose: Implementation of textX language in Arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# The idea for this language is shamelessly stolen from the Xtext language
# but there are some subtle differences in both syntax and semantics.
# To make things clear I have named this language textX ;)
#######################################################################

from collections import namedtuple

from arpeggio import StrMatch, Optional, ZeroOrMore, OneOrMore, Sequence,\
    OrderedChoice, RegExMatch, NoMatch, EOF,\
    SemanticAction,ParserPython, Combine, Parser, SemanticActionSingleChild,\
    SemanticActionBodyWithBraces
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _


# textX grammar
def textx_model():          return ZeroOrMore(rule), EOF
def rule():                 return [metaclass, enum]
def enum():                 return enum_kwd, ident, ':', enum_literal,\
                                    ZeroOrMore("|", enum_literal), ';'
def enum_literal():         return ident, '=', str_match
def metaclass():            return metaclass_name, ":", choice, ';'
def metaclass_name():       return ident

def choice():               return sequence, ZeroOrMore("|", sequence)
def sequence():             return OneOrMore(expr)

def expr():                 return [assignment, terminal_match, rule_match,
                                    bracketed_choice],\
                                    Optional(repeat_operator)
def bracketed_choice():     return '(', choice, ')'
def repeat_operator():      return ['*', '?', '+']

# Assignment
def assignment():           return attribute, assignment_op, assignment_rhs
def attribute():            return ident
def assignment_op():        return ["=", "*=", "+=", "?="]
def assignment_rhs():       return [rule_ref, list_match, terminal_match, bracketed_choice]

# Match
def match():                return [terminal_match, list_match, rule_ref]
def terminal_match():       return [str_match, re_match]
def str_match():            return [("'", _(r"((\\')|[^'])*"),"'"),\
                                    ('"', _(r'((\\")|[^"])*'),'"')]
def re_match():             return "/", _(r"((\\/)|[^/])*"), "/"

def list_match():           return "{", rule_ref, Optional(list_separator), '}'
def list_separator():       return terminal_match

# Rule reference
def rule_ref():             return [rule_match, rule_link]
def rule_match():           return ident
def rule_link():            return '[', rule_name, ']'
#def rule_choice():          return rule_name, ZeroOrMore('|', rule_name)
def rule_name():            return ident

def ident():                return _(r'\w+')
def enum_kwd():             return 'enum'

# Comments
def comment():              return [comment_line, comment_block]
def comment_line():         return _(r'//.*$')
def comment_block():        return _(r'/\*(.|\n)*?\*/')


# Special rules - primitive types
ID      = _(r'[^\d\W]\w*\b', rule='ID', root=True)
INT     = _(r'[-+]?[0-9]+', rule='INT', root=True)
FLOAT   = _(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'FLOAT', root=True)
STRING  = _(r'("[^"]*")|(\'[^\']*\')', 'STRING', root=True)

class RuleMatchCrossRef(object):
    """Helper class used for cross reference resolving."""
    def __init__(self, rule_name, position):
        self.rule_name = rule_name
        self.position = position


# TextX Exceptions
class TextXError(Exception):
    pass


class TextXSemanticError(TextXError):
    pass


class TextXSyntaxError(TextXError):
    pass


# TextX semantic actions
class TextXModelSA(SemanticAction):
    def first_pass(self, parser, node, children):

        class TextXLanguageParser(Parser):
            """
            Parser created from textual textX language description.
            Semantic actions for this parser will construct object
            graph representing model on the given language.
            """
            def __init__(self, *args, **kwargs):
                super(TextXLanguageParser, self).__init__(*args, **kwargs)

                # By default first rule is starting rule
                self.parser_model = children[0]
                self.comments_model = parser._peg_rules.get('__comment', None)

                self.debug = parser.debug

            def _parse(self):
                try:
                    return self.parser_model.parse(self)
                except NoMatch as e:
                    raise TextXSyntaxError(str(e))

        textx_parser = TextXLanguageParser()

        textx_parser._metaclasses = parser._metaclasses
        textx_parser._peg_rules = parser._peg_rules

        return textx_parser

    def second_pass(self, parser, textx_parser):
        """Cross reference resolving for parser model."""

        resolved_set = set()

        def resolve(node):
            """Recursively resolve peg rule references."""
            if node in resolved_set or not hasattr(node, 'nodes'):
                return

            resolved_set.add(node)

            def _inner_resolve(rule):
                if type(rule) == RuleMatchCrossRef:
                    if rule.rule_name in textx_parser._peg_rules:
                        rule_name = rule.rule_name
                        rule = textx_parser._peg_rules[rule.rule_name]

                        # Cached rule may be crossref also.
                        while type(rule) == RuleMatchCrossRef:
                            rule_name = rule.rule_name
                            rule = _inner_resolve(rule)
                            # Rewrite rule in the rules map
                            textx_parser._peg_rules[rule_name] = rule

                return rule

            for idx, rule in enumerate(node.nodes):
                # If crossref resolve
                if type(rule) == RuleMatchCrossRef:
                    rule = _inner_resolve(rule)
                    node.nodes[idx] = _inner_resolve(rule)

                # If still unresolved raise exception
                if type(rule) == RuleMatchCrossRef:
                    raise TextXSemanticError('Unexisting rule "{}" at position {}.'\
                            .format(rule.rule_name, parser.pos_to_linecol(rule.position)))

                # Depth-First processing
                resolve(rule)

        resolve(textx_parser.parser_model)

        return textx_parser

textx_model.sem = TextXModelSA()


def metaclass_SA(parser, node, children):
    rule_name, rule = children
    rule.rule = rule_name
    rule.root = True

    # Do some name mangling for comment rule
    # to prevent refererencing from other rules
    if rule_name.lower() == "comment":
        rule_name = "__comment"

    parser._peg_rules[rule_name] = rule
    return rule
metaclass.sem = metaclass_SA

def metaclass_name_SA(parser, node, children):
    class Meta(object):
        """Dynamic metaclass."""
        pass
    name = str(node)
    cls = Meta
    cls.__name__ = name
    # TODO: Attributes and inheritance
    parser._metaclasses[name] = cls
    parser._current_metaclass = cls

    # First rule will be the root of the meta-model
    if not parser.root_rule_name:
        parser.root_rule_name = name

    return name
metaclass_name.sem = metaclass_name_SA

def sequence_SA(parser, node, children):
    return Sequence(nodes=children[:])
sequence.sem = sequence_SA

def choice_SA(parser, node, children):
    return OrderedChoice(nodes=children[:])
choice.sem = choice_SA

def assignment_SA(parser, node, children):
    #TODO: Register assignment on metaclass
    # Implement semantic for addition
    rhs = children[2]
    op = children[1]
    if op == '+=':
        return OneOrMore(nodes=[rhs])
    elif op == '*=':
        return ZeroOrMore(nodes=[rhs])
    elif op == '?=':
        return Optional(nodes=[rhs])
    else:
        return children[2]
assignment.sem = assignment_SA

def expr_SA(parser, node, children):
    if children[1] == '?':
        return Optional(nodes=[children[0]])
    elif children[1] == '*':
        return ZeroOrMore(nodes=[children[0]])
    elif children[1] == '+':
        return OneOrMore(nodes=[children[0]])
    else:
        TextXSemanticError('Unknown repetition operand "{}" at {}'\
                .format(children[1], str(parser.pos_to_linecol(node[1].position))))
expr.sem = expr_SA

def str_match_SA(parser, node, children):
    return StrMatch(children[0], ignore_case=parser.ignore_case)
str_match.sem = str_match_SA

def re_match_SA(parser, node, children):
    to_match = children[0]
    regex = RegExMatch(to_match, ignore_case=parser.ignore_case)
    try:
        regex.compile()
    except Exception as e:
        raise TextXSyntaxError("{} at {}".format(str(e),\
            str(parser.pos_to_linecol(node[1].position))))
    return regex
re_match.sem = re_match_SA

def rule_match_SA(parser, node, children):
    return RuleMatchCrossRef(str(node), node.position)
rule_match.sem = rule_match_SA

def rule_link_SA(parser, node, children):
    # TODO: In analisys during model parsing this will be a link to some other object
    # identified by target metaclass ID
    return ID
rule_link.sem = rule_link_SA

def list_match_SA(parser, node, children):
    if len(children)==1:
        return children[0]
    else:
        match = children[0]
        separator = children[1]
        return Sequence(nodes=[children[0],
                ZeroOrMore(nodes=Sequence(nodes=[separator, match]))])
list_match.sem = list_match_SA

# Default actions
bracketed_choice.sem = SemanticActionSingleChild()


def get_parser(language_def, ignore_case=True, debug=False):
    # First create parser for TextX descriptions
    parser = ParserPython(textx_model, comment_def=comment,
            ignore_case=ignore_case, reduce_tree=True, debug=debug)

    # This is used during parser construction phase.
    parser._metaclasses = {}
    parser._peg_rules = {
            'ID': ID,
            'INT': INT,
            'FLOAT': FLOAT,
            'STRING': STRING,
            }
    for regex in parser._peg_rules.values():
        regex.compile()
    parser._current_metaclass = None
    parser.root_rule_name = None

    # Parse language description with TextX parser
    try:
        parse_tree = parser.parse(language_def)
    except NoMatch as e:
        raise TextXSyntaxError(str(e))

    # Construct new parser based on the given language description.
    # This parser will have semantic actions in place to create
    # object model from the textx textual representations.
    lang_parser = parser.getASG()

    if debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(lang_parser.parser_model,\
                "{}_parser_model.dot".format(parser.root_rule_name))

    return lang_parser


