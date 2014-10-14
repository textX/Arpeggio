# -*- coding: utf-8 -*-
#######################################################################
# Name: peg.py
# Purpose: Implementing PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import print_function, unicode_literals
import sys
if sys.version < '3':
    text = unicode
else:
    text = str

import copy
from arpeggio import *
from arpeggio import RegExMatch as _

__all__ = ['ParserPEG']


# PEG syntax rules
def peggrammar():       return OneOrMore(rule), EOF
def rule():             return rule_name, LEFT_ARROW, ordered_choice, ";"
def ordered_choice():   return sequence, ZeroOrMore(SLASH, sequence)
def sequence():         return OneOrMore(prefix)
def prefix():           return Optional([AND,NOT]), sufix
def sufix():            return expression, Optional([QUESTION, STAR, PLUS])
def expression():       return [regex, rule_crossref,
                                (OPEN, ordered_choice, CLOSE),
                                str_match]

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


class PEGVisitor(PTNodeVisitor):
    """
    Visitor that transforms parse tree to a PEG parser for the given language.
    """

    def __init__(self, root_rule_name, comment_rule_name, ignore_case,
                 *args, **kwargs):
        super(PEGVisitor, self).__init__(*args, **kwargs)
        self.root_rule_name = root_rule_name
        self.comment_rule_name = comment_rule_name
        self.ignore_case = ignore_case
        # Used for linking phase
        self.peg_rules = {
            "EOF": EndOfFile()
        }

    def visit_peggrammar(self, node, children):
        def _resolve(node):

            def get_rule_by_name(rule_name):
                if rule_name in self.peg_rules:
                    return self.peg_rules[rule_name]
                else:
                    raise SemanticError("Rule \"{}\" does not exists."
                                        .format(rule_name))

            def resolve_rule_by_name(rule_name):
                    if self.debug:
                        print("Resolving crossref {}".format(rule_name))
                    resolved_rule = get_rule_by_name(rule_name)
                    while type(resolved_rule) is CrossRef:
                        target_rule = resolved_rule.target_rule_name
                        resolved_rule = get_rule_by_name(target_rule)
                    # If resolved rule hasn't got the same name it
                    # should be cloned and preserved in the peg_rules cache
                    if resolved_rule.rule_name != rule_name:
                        resolved_rule = copy.copy(resolved_rule)
                        resolved_rule.rule_name = rule_name
                        self.peg_rules[rule_name] = resolved_rule
                        if self.debug:
                            print("Resolving: cloned to {} = > {}"
                                  .format(resolved_rule.rule_name,
                                          resolved_rule.name))
                    return resolved_rule

            if isinstance(node, CrossRef):
                # The root rule is a cross-ref
                resolved_rule = resolve_rule_by_name(node.target_rule_name)
                if resolved_rule not in self.resolved:
                    self.resolved.add(resolved_rule)
                    _resolve(resolved_rule)
                return resolved_rule
            else:
                # Resolve children nodes
                for i, n in enumerate(node.nodes):
                    node.nodes[i] = _resolve(n)
                self.resolved.add(node)
                return node

        # Find root and comment rules
        self.resolved = set()
        comment_rule = None
        for rule in children:
            if rule.rule_name == self.root_rule_name:
                root_rule = _resolve(rule)
            if rule.rule_name == self.comment_rule_name:
                comment_rule = _resolve(rule)

        assert root_rule, "Root rule not found!"
        return root_rule, comment_rule

    def visit_rule(self, node, children):
        rule_name = children[0]
        if len(children) > 2:
            retval = Sequence(nodes=children[1:])
        else:
            retval = children[1]

        retval.rule_name = rule_name
        retval.root = True

        # Keep a map of parser rules for cross reference
        # resolving.
        self.peg_rules[rule_name] = retval
        return retval

    def visit_sequence(self, node, children):
        if len(children) > 1:
            return Sequence(nodes=children[:])
        else:
            # If only one child rule exists reduce.
            return children[0]

    def visit_ordered_choice(self, node, children):
        if len(children) > 1:
            retval = OrderedChoice(nodes=children[:])
        else:
            # If only one child rule exists reduce.
            retval = children[0]
        return retval

    def visit_prefix(self, node, children):
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

    def visit_sufix(self, node, children):
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

    def visit_rule_crossref(self, node, children):
        return CrossRef(node.value)

    def visit_regex(self, node, children):
        match = RegExMatch(children[0],
                           ignore_case=self.ignore_case)
        match.compile()
        return match

    def visit_str_match(self, node, children):
        match_str = node.value[1:-1]
        match_str = match_str.replace("\\'", "'")
        match_str = match_str.replace("\\\\", "\\")
        return StrMatch(match_str, ignore_case=self.ignore_case)


class ParserPEG(Parser):

    def __init__(self, language_def, root_rule_name, comment_rule_name=None,
                 *args, **kwargs):
        """
        Constructs parser from textual PEG definition.

        Args:
            language_def (str): A string describing language grammar using
                PEG notation.
            root_rule_name(str): The name of the root rule.
            comment_rule_name(str): The name of the rule for comments.
        """
        super(ParserPEG, self).__init__(*args, **kwargs)
        self.root_rule_name = root_rule_name
        self.comment_rule_name = comment_rule_name

        # PEG Abstract Syntax Graph
        self.parser_model, self.comments_model = self._from_peg(language_def)
        # Comments should be optional and there can be more of them
        if self.comments_model:
            self.comments_model.root = True
            self.comments_model.rule_name = comment_rule_name

        # In debug mode export parser model to dot for
        # visualization
        if self.debug:
            from arpeggio.export import PMDOTExporter
            root_rule = self.parser_model.rule_name
            PMDOTExporter().exportFile(
                self.parser_model, "{}_peg_parser_model.dot".format(root_rule))

    def _parse(self):
        return self.parser_model.parse(self)

    def _from_peg(self, language_def):
        parser = ParserPython(peggrammar, comment, reduce_tree=False,
                              debug=self.debug)
        parser.root_rule_name = self.root_rule_name
        parse_tree = parser.parse(language_def)

        return visit_parse_tree(parse_tree, PEGVisitor(self.root_rule_name,
                                                       self.comment_rule_name,
                                                       self.ignore_case,
                                                       debug=self.debug))
