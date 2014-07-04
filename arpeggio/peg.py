# -*- coding: utf-8 -*-
#######################################################################
# Name: peg.py
# Purpose: Implementing PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import print_function
from kivy.lang import ParserException

__all__ = ['ParserPEG']

from arpeggio import *
from arpeggio import RegExMatch as _


# PEG Lexical rules
def LEFT_ARROW():       return "<-"
def SLASH():            return "/"
def STAR():             return "*"
def QUESTION():         return "?"
def PLUS():             return "+"
def AND():              return "&"
def NOT():              return "!"
def OPEN():             return "("
def CLOSE():            return ")"
def regex():            return "r'", _(r"(\\\'|[^\'])*"),"'"
def rule_identifier():       return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")
#def literal():          return [_(r"\'(\\\'|[^\'])*\'"),_(r'"[^"]*"')]
def literal():          return _(r'(\'(\\\'|[^\'])*\')|("[^"]*")')
def comment():          return "//", _(".*\n")

# PEG syntax rules
def grammar():          return OneOrMore(rule), EOF
def rule():             return rule_identifier, LEFT_ARROW, ordered_choice, ";"
def ordered_choice():   return sequence, ZeroOrMore(SLASH, sequence)
def sequence():         return OneOrMore(prefix)
def prefix():           return Optional([AND,NOT]), sufix
def sufix():            return expression, Optional([QUESTION, STAR, PLUS])
def expression():       return [regex,(rule_identifier, Not(LEFT_ARROW)),
                                (OPEN, ordered_choice, CLOSE),
                                literal]


# ------------------------------------------------------------------
# PEG Semantic Actions

class PEGSemanticAction(SemanticAction):
    def _resolve(self, parser, rule_name):
        if rule_name in parser.peg_rules:
            if parser.debug:
                print("Resolving reference {}".format(rule_name))
            return parser.peg_rules[rule_name]
        else:
            raise SemanticError("Rule \"{}\" does not exists."
                                .format(rule_name))

    def second_pass(self, parser, node):
        if isinstance(node, CrossRef):
            return self._resolve(parser, node.rule_name)
        elif isinstance(node, ParsingExpression):
            for i, n in enumerate(node.nodes):
                if isinstance(n, CrossRef):
                    node[i] = self._resolve(parser, n.rule_name)
            return node
        else:
            raise SemanticError("Invalid type '{}' after first pass."
                                .format(type(node)))


class SemGrammar(SemanticAction):
    def first_pass(self, parser, node, children):
        return parser.peg_rules[parser.root_rule_name]


class SemRule(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        rule_name = children[0]
        if len(children) > 4:
            retval = Sequence(nodes=children[2:-1])
        else:
            retval = children[2]
        retval.rule = rule_name
        retval.root = True

        if not hasattr(parser, "peg_rules"):
            parser.peg_rules = {}   # Used for linking phase
            parser.peg_rules["EndOfFile"] = EndOfFile()

        parser.peg_rules[rule_name] = retval
        return retval


class SemSequence(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        if len(children) > 1:
            return Sequence(nodes=children)
        else:
            return children[0]


class SemOrderedChoice(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        if len(children) > 1:
            retval = OrderedChoice(nodes=children[::2])
        else:
            retval = children[0]
        return retval


class SemPrefix(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        if len(children) == 2:
            if children[0] == NOT():
                retval = Not()
            else:
                retval = And()
            if type(children[1]) is list:
                retval.nodes = children[1]
            else:
                retval.nodes = [children[1]]
        else:
            retval = children[0]

        return retval


class SemSufix(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        if len(children) == 2:
            if children[1] == STAR():
                retval = ZeroOrMore(children[0])
            elif children[1] == QUESTION():
                retval = Optional(children[0])
            else:
                retval = OneOrMore(children[0])
            if type(children[0]) is list:
                retval.nodes = children[0]
            else:
                retval.nodes = [children[0]]
        else:
            retval = children[0]

        return retval


class SemExpression(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        if len(children) == 1:
            return children[0]
        else:
            return children[1]


class SemIdentifier(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        return super(SemIdentifier, self).first_pass(parser, node, children)


class SemRegEx(SemanticAction):
    def first_pass(self, parser, node, children):
        return RegExMatch(children[1])


class SemLiteral(SemanticAction):
    def first_pass(self, parser, node, children):
        match_str = node.value[1:-1]
        match_str = match_str.replace("\\'", "'")
        match_str = match_str.replace("\\\\", "\\")
        return StrMatch(match_str)


grammar.sem = SemGrammar()
rule.sem = SemRule()
ordered_choice.sem = SemOrderedChoice()
sequence.sem = SemSequence()
prefix.sem = SemPrefix()
sufix.sem = SemSufix()
expression.sem = SemExpression()
regex.sem = SemRegEx()
rule_identifier.sem = SemIdentifier()
literal.sem = SemLiteral()


class ParserPEG(Parser):
    def __init__(self, language_def, root_rule_name, comment_rule_name=None,
                 *args, **kwargs):
        super(ParserPEG, self).__init__(*args, **kwargs)
        self.root_rule_name = root_rule_name

        # PEG Abstract Syntax Graph
        self.parser_model = self._from_peg(language_def)

        # Comments should be optional and there can be more of them
        if self.comments_model: # and not isinstance(self.comments_model, ZeroOrMore):
            self.comments_model.root = True
            self.comments_model.rule = comment_rule_name

    def _parse(self):
        return self.parser_model.parse(self)

    def _from_peg(self, language_def):
        parser = ParserPython(grammar, comment, reduce_tree=False, debug=True)
        parser.root_rule_name = self.root_rule_name
        parser.parse(language_def)
        return parser.getASG()
