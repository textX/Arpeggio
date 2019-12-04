#######################################################################
# Name: visitor_peg.py
# Purpose: Implementing PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2017 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

# stdlib
import codecs
import copy
import re

# proj
from . import error_classes
from . import peg_expressions
from . import peg_lexical
from . import peg_utils
from . import visitor_base


# Escape sequences supported in PEG literal string matches
PEG_ESCAPE_SEQUENCES_RE = re.compile(r"""
    \\ ( [\n\\'"abfnrtv]  |  # \\x single-character escapes
         [0-7]{1,3}       |  # \\ooo octal escape
         x[0-9A-Fa-f]{2}  |  # \\xXX hex escape
         u[0-9A-Fa-f]{4}  |  # \\uXXXX hex escape
         U[0-9A-Fa-f]{8}  |  # \\UXXXXXXXX hex escape
         N\{[- 0-9A-Z]+\}    # \\N{name} Unicode name or alias
       )
    """, re.VERBOSE | re.UNICODE)


class PEGVisitor(visitor_base.PTNodeVisitor):
    """
    Visitor that transforms parse tree to a PEG parser for the given language.
    """

    def __init__(self, root_rule_name, comment_rule_name, ignore_case,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_rule_name = root_rule_name
        self.comment_rule_name = comment_rule_name
        self.ignore_case = ignore_case
        # Used for linking phase
        self.peg_rules = {"EOF": peg_expressions.EndOfFile()}

    def visit_peggrammar(self, node, children):

        def _resolve(node):
            """
            Resolves CrossRefs from the parser model.
            """

            if node in self.resolved:
                return node
            self.resolved.add(node)

            def get_rule_by_name(rule_name):
                try:
                    return self.peg_rules[rule_name]
                except KeyError:
                    raise error_classes.SemanticError("Rule \"{}\" does not exists.".format(rule_name))

            def resolve_rule_by_name(rule_name):
                if self.debug:
                    self.dprint("Resolving crossref {}".format(rule_name))

                resolved_rule = get_rule_by_name(rule_name)
                while type(resolved_rule) is peg_utils.CrossRef:
                    target_rule = resolved_rule.target_rule_name
                    resolved_rule = get_rule_by_name(target_rule)

                # If resolved rule hasn't got the same name it
                # should be cloned and preserved in the peg_rules cache
                if resolved_rule.rule_name != rule_name:
                    resolved_rule = copy.copy(resolved_rule)
                    resolved_rule.rule_name = rule_name
                    self.peg_rules[rule_name] = resolved_rule
                    if self.debug:
                        self.dprint("Resolving: cloned to {} = > {}"
                                    .format(resolved_rule.rule_name,
                                            resolved_rule.name))
                return resolved_rule

            if isinstance(node, peg_utils.CrossRef):
                # The root rule is a cross-ref
                resolved_rule = resolve_rule_by_name(node.target_rule_name)
                return _resolve(resolved_rule)
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
            retval = peg_expressions.Sequence(nodes=children[1:])
        else:
            retval = children[1]

        retval.rule_name = rule_name
        retval.root = True

        # Keep a map of parser rules for cross reference
        # resolving.
        self.peg_rules[rule_name] = retval
        return retval

    @staticmethod
    def visit_sequence(node, children):
        if len(children) > 1:
            return peg_expressions.Sequence(nodes=children[:])
        else:
            # If only one child rule exists reduce.
            return children[0]

    @staticmethod
    def visit_ordered_choice(node, children):
        if len(children) > 1:
            retval = peg_expressions.OrderedChoice(nodes=children[:])
        else:
            # If only one child rule exists reduce.
            retval = children[0]
        return retval

    @staticmethod
    def visit_prefix(node, children):
        if len(children) == 2:
            if children[0] == peg_lexical.NOT:
                retval = peg_expressions.Not()
            else:
                retval = peg_expressions.And()
            if type(children[1]) is list:
                retval.nodes = children[1]
            else:
                retval.nodes = [children[1]]
        else:
            # If there is no optional prefix reduce.
            retval = children[0]

        return retval

    @staticmethod
    def visit_sufix(node, children):
        if len(children) == 2:
            if type(children[0]) is list:
                nodes = children[0]
            else:
                nodes = [children[0]]
            if children[1] == peg_lexical.ZERO_OR_MORE:
                retval = peg_expressions.ZeroOrMore(nodes=nodes)
            elif children[1] == peg_lexical.ONE_OR_MORE:
                retval = peg_expressions.OneOrMore(nodes=nodes)
            elif children[1] == peg_lexical.OPTIONAL:
                retval = peg_expressions.Optional(nodes=nodes)
            else:
                retval = peg_expressions.UnorderedGroup(nodes=nodes[0].nodes)
        else:
            retval = children[0]

        return retval

    @staticmethod
    def visit_rule_crossref(node, children):
        return peg_utils.CrossRef(node.value)

    def visit_regex(self, node, children):
        match = peg_expressions.RegExMatch(children[0], ignore_case=self.ignore_case)
        match.compile()
        return match

    def visit_str_match(self, node, children):
        match_str = node.value[1:-1]

        # Scan the string literal, and sequentially match those escape
        # sequences which are syntactically valid Python. Attempt to convert
        # those, raising ``GrammarError`` for any semantically invalid ones.
        def decode_escape(match):
            try:
                return codecs.decode(match.group(0), "unicode_escape")
            except UnicodeDecodeError:
                raise error_classes.GrammarError("Invalid escape sequence '%s'." %
                                                 match.group(0))
        match_str = PEG_ESCAPE_SEQUENCES_RE.sub(decode_escape, match_str)

        return peg_expressions.StrMatch(match_str, ignore_case=self.ignore_case)
