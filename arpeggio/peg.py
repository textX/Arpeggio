# -*- coding: utf-8 -*-
#######################################################################
# Name: peg.py
# Purpose: Implementing PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import print_function
import copy
from arpeggio import *
from arpeggio import RegExMatch as _
from arpeggio.export import PMDOTExporter, PTDOTExporter

__all__ = ['ParserPEG']


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
def rule_name():        return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")
def rule_crossref():    return rule_name
#def literal():          return [_(r"\'(\\\'|[^\'])*\'"),_(r'"[^"]*"')]
def str_match():        return _(r'(\'(\\\'|[^\'])*\')|("[^"]*")')
def comment():          return "//", _(".*\n")

# PEG syntax rules
def peggrammar():      return OneOrMore(rule), EOF
def rule():             return rule_name, LEFT_ARROW, ordered_choice, ";"
def ordered_choice():   return sequence, ZeroOrMore(SLASH, sequence)
def sequence():         return OneOrMore(prefix)
def prefix():           return Optional([AND,NOT]), sufix
def sufix():            return expression, Optional([QUESTION, STAR, PLUS])
def expression():       return [regex, rule_crossref,
                                (OPEN, ordered_choice, CLOSE),
                                str_match]


# ------------------------------------------------------------------
# PEG Semantic Actions

class PEGSemanticAction(SemanticAction):

    def _resolve(self, parser, rule_name):

        if rule_name in parser.peg_rules:
            resolved_rule = parser.peg_rules[rule_name]
            if type(resolved_rule) is CrossRef:
                resolved_rule = self._resolve(parser, resolved_rule.rule_name)

            if parser.debug:
                print("Resolving: CrossRef {} => {}".format(rule_name, 
                    resolved_rule.name))

            return resolved_rule
        else:
            raise SemanticError("Rule \"{}\" does not exists."
                                .format(rule_name))

    def second_pass(self, parser, node):
        '''
        Resolving cross-references in second pass.
        '''
        if parser.debug:
            print("Second pass:", type(node), str(node))

        if isinstance(node, ParsingExpression):

            for i, n in enumerate(node.nodes):
                if isinstance(n, CrossRef):
                    resolved_rule = self._resolve(parser, n.rule_name)

                    # If resolved rule hasn't got the same name it
                    # should be cloned and preserved in the peg_rules cache
                    if resolved_rule.rule_name != n.rule_name:
                        resolved_rule = copy.copy(resolved_rule)
                        resolved_rule.rule_name = n.rule_name
                        parser.peg_rules[resolved_rule.rule_name] = resolved_rule

                        if parser.debug:
                            print("Resolving: cloned to {} = > {}"\
                                    .format(resolved_rule.rule_name, resolved_rule.name))

                    node.nodes[i] = resolved_rule

            return node

        elif not isinstance(node, CrossRef):
            raise SemanticError("Invalid type '{}'({}) after first pass."
                                .format(type(node), str(node)))


class SemGrammar(SemanticAction):
    def first_pass(self, parser, node, children):
        return parser.peg_rules[parser.root_rule_name]


class SemRule(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        rule_name = children[0]
        if len(children) > 2:
            retval = Sequence(nodes=children[1:])
        else:
            retval = children[1]
        retval.rule_name = rule_name
        retval.root = True

        if not hasattr(parser, "peg_rules"):
            parser.peg_rules = {}   # Used for linking phase
            parser.peg_rules["EOF"] = EndOfFile()

        # Keep a map of parser rules for cross reference
        # resolving.
        parser.peg_rules[rule_name] = retval
        return retval


class SemSequence(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        if len(children) > 1:
            return Sequence(nodes=children[:])
        else:
            # If only one child rule exists reduce.
            return children[0]


class SemOrderedChoice(PEGSemanticAction):
    def first_pass(self, parser, node, children):
        if len(children) > 1:
            retval = OrderedChoice(nodes=children[:])
        else:
            # If only one child rule exists reduce.
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
            # If there is no optional prefix reduce.
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
        return children[0]


class SemRuleCrossRef(SemanticAction):
    def first_pass(self, parser, node, children):
        return CrossRef(node.value)


class SemRegEx(SemanticAction):
    def first_pass(self, parser, node, children):
        match = RegExMatch(children[0],
                ignore_case=parser.ignore_case)
        match.compile()
        return match

class SemStrMatch(SemanticAction):
    def first_pass(self, parser, node, children):
        match_str = node.value[1:-1]
        match_str = match_str.replace("\\'", "'")
        match_str = match_str.replace("\\\\", "\\")
        return StrMatch(match_str, ignore_case=parser.ignore_case)


peggrammar.sem = SemGrammar()
rule.sem = SemRule()
ordered_choice.sem = SemOrderedChoice()
sequence.sem = SemSequence()
prefix.sem = SemPrefix()
sufix.sem = SemSufix()
expression.sem = SemExpression()
rule_crossref.sem = SemRuleCrossRef()
regex.sem = SemRegEx()
str_match.sem = SemStrMatch()


class ParserPEG(Parser):
    def __init__(self, language_def, root_rule_name, comment_rule_name=None,
                 *args, **kwargs):
        super(ParserPEG, self).__init__(*args, **kwargs)
        self.root_rule_name = root_rule_name

        # PEG Abstract Syntax Graph
        self.parser_model = self._from_peg(language_def)

        # In debug mode export parser model to dot for
        # visualization
        if self.debug:
            from arpeggio.export import PMDOTExporter
            root_rule = self.parser_model.rule_name
            PMDOTExporter().exportFile(self.parser_model,
                                    "{}_peg_parser_model.dot".format(root_rule))

        # Comments should be optional and there can be more of them
        if self.comments_model: # and not isinstance(self.comments_model, ZeroOrMore):
            self.comments_model.root = True
            self.comments_model.rule_name = comment_rule_name

    def _parse(self):
        return self.parser_model.parse(self)

    def _from_peg(self, language_def):
        parser = ParserPython(peggrammar, comment, reduce_tree=False, debug=self.debug)
        parser.root_rule_name = self.root_rule_name
        parser.parse(language_def)

        return parser.getASG()
