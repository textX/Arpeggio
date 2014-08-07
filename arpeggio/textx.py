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
    OrderedChoice, RegExMatch, EOF,\
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
def assignment_rhs():       return [rule_ref, list_match, terminal_match]

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
def rule_link():            return '[', rule_choice, ']'
def rule_choice():          return rule_name, ZeroOrMore('|', rule_name)
def rule_name():            return ident

def ident():                return _(r'\w+')
def enum_kwd():             return 'enum'

# Comments
def comment():              return [comment_line, comment_block]
def comment_line():         return _(r'//.*$')
def comment_block():        return _(r'/\*(.|\n)*?\*/')



class RuleMatchCrossRef(object):
    """Helper class used for cross reference resolving."""
    def __init__(self, rule_name, position):
        self.rule_name = rule_name
        self.position = position


class TextXSemanticError(Exception):
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
                self.parser_model = Sequence(nodes=children[:], rule='model', root=True)
                self.comments_model = parser._peg_rules.get('__comment', None)

            def _parse(self):
                return self.parser_model.parse(self)

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


class MetaClassSA(SemanticAction):
    def first_pass(self, parser, node, children):
        rule_name, rule = children

        # Do some name mangling for comment rule
        # to prevent refererencing from other rules
        if rule_name.lower() == "comment":
            rule_name = "__comment"

        parser._peg_rules[rule_name] = rule
        return rule


class MetaClassNameSA(SemanticAction):
    def first_pass(self, parser, node, children):
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


class SequenceSA(SemanticAction):
    def first_pass(self, parser, node, children):
        return Sequence(nodes=children[:])


class ChoiceSA(SemanticAction):
    def first_pass(self, parser, node, children):
        return OrderedChoice(nodes=children[:])


class AssignmentSA(SemanticAction):
    def first_pass(self, parser, node, children):
        #TODO: Register assignment on metaclass
        return children[2]


class ExprSA(SemanticAction):
    def first_pass(self, parser, node, children):
        if children[1] == '?':
            return Optional(nodes=[children[0]])
        elif children[1] == '*':
            return ZeroOrMore(nodes=[children[0]])
        elif children[1] == '+':
            return OneOrMore(nodes=[children[0]])
        else:
            TextXSemanticError('Unknown repetition operand "{}" at {}'\
                    .format(children[1], str(parser.pos_to_linecol(node[1].position))))


class StrMatchSA(SemanticAction):
    def first_pass(self, parser, node, children):
        return StrMatch(children[0], ignore_case=parser.ignore_case)


class REMatchSA(SemanticAction):
    def first_pass(self, parser, node, children):
        to_match = children[0]
        print("TOMATCH:", to_match)
        regex = RegExMatch(to_match, ignore_case=parser.ignore_case)
        regex.compile()
        return regex


class RuleMatchSA(SemanticAction):
    def first_pass(self, parser, node, children):
        return RuleMatchCrossRef(str(node), node.position)



textx_model.sem = TextXModelSA()
metaclass.sem = MetaClassSA()
metaclass_name.sem = MetaClassNameSA()
sequence.sem = SequenceSA()
choice.sem = ChoiceSA()
bracketed_choice.sem = SemanticActionSingleChild()
expr.sem = ExprSA()
str_match.sem = StrMatchSA()
re_match.sem = REMatchSA()
rule_match.sem = RuleMatchSA()


def get_parser(language_def, ignore_case=True, debug=False):
    # First create parser for TextX descriptions
    parser = ParserPython(textx_model, comment_def=comment,
            ignore_case=ignore_case, reduce_tree=True, debug=debug)

    # This is used during parser construction phase.
    parser._metaclasses = {}
    parser._peg_rules = {
            # Special rules - primitive types
            'ID': _(r'[^\d\W]\w*\b'),
            'INT': _(r'[-+]?[0-9]+'),
            'FLOAT': _(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'),
            'STRING': _(r'("[^"]*")|(\'[^\']*\')')
            }
    for regex in parser._peg_rules.values():
        regex.compile()
    parser._current_metaclass = None
    parser.root_rule_name = None

    # Parse language description with TextX parser
    parse_tree = parser.parse(language_def)

    # Construct new parser based on the given language description.
    # This parser will have semantic actions in place to create
    # object model from the textx textual representations.
    lang_parser = parser.getASG()

    if debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(lang_parser.parser_model,\
                "{}_parser_model.dot".format(parser.root_rule_name))

    return lang_parser


