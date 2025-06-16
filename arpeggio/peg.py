#######################################################################
# Name: peg.py
# Purpose: Implementing PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@ya.ru>
# Copyright: (c) 2009-2017 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2025 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@ya.ru>
# License: MIT License
#######################################################################

import codecs
import copy
import re

from arpeggio import (
    EOF,
    And,
    CrossRef,
    EndOfFile,
    GrammarError,
    Not,
    OneOrMore,
    Optional,
    OrderedChoice,
    Parser,
    ParserPython,
    PTNodeVisitor,
    SemanticError,
    Sequence,
    StrMatch,
    UnorderedGroup,
    ZeroOrMore,
    visit_parse_tree,
    Match,
    MatchActions,
    MatchState,
)
from arpeggio import RegExMatch as _

__all__ = ['ParserPEG']

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
CALL_START = "{"
CALL_END = "}"
CALL_DELIMITER = ','
STATE_START = '['
STATE_END = ']'



# PEG syntax rules
def peggrammar():       return OneOrMore(rule), EOF
def rule():             return rule_name, LEFT_ARROW, ordered_choice, ";"
def ordered_choice():   return sequence, ZeroOrMore(ORDERED_CHOICE, sequence)
def sequence():         return OneOrMore(full_expression)
def operation():        return rule_crossref, calls
def full_expression():  return Optional([AND, NOT]), expression_with_state
def expression_with_state():    return Optional(state), repeated_expression
def repeated_expression():      return expression, Optional([OPTIONAL,
                                                             ZERO_OR_MORE,
                                                             ONE_OR_MORE,
                                                             UNORDERED_GROUP])
def expression():       return [operation, regex, rule_crossref,
                                (OPEN, ordered_choice, CLOSE),
                                str_match]

# PEG Lexical rules
def regex():            return _(r"""(r'[^'\\]*(?:\\.[^'\\]*)*')|"""
                                 r'''(r"[^"\\]*(?:\\.[^"\\]*)*")''')
def rule_name():        return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")
def rule_crossref():    return rule_name
def str_match():        return _(r'''(?s)('[^'\\]*(?:\\.[^'\\]*)*')|'''
                                     r'''("[^"\\]*(?:\\.[^"\\]*)*")''')
def comment():          return _("//.*\n", multiline=False)

def calls():            return CALL_START, call, ZeroOrMore([CALL_DELIMITER, call]), CALL_END
def call():             return OneOrMore(call_argument)
def call_argument():    return _(r'[^\} \t,]+')

def state():            return STATE_START, state_name, STATE_END
def state_name():       return _(r'[a-zA-Z_][a-zA-Z_0-9]*')


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


class PEGVisitor(PTNodeVisitor):
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
        self.peg_rules = {
            "EOF": EndOfFile()
        }

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
                except KeyError as e:
                    raise SemanticError(f"Rule \"{rule_name}\" does not exists.") from e

            def resolve_rule_by_name(rule_name):

                    if self.debug:
                        self.dprint(f"Resolving crossref {rule_name}")

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
                            self.dprint(f"Resolving: cloned to "
                                        f"{resolved_rule.rule_name} "
                                        f"=> {resolved_rule.name}")
                    return resolved_rule

            if isinstance(node, CrossRef):
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
        retval = Sequence(nodes=children[1:]) if len(children) > 2 else children[1]
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
        retval = OrderedChoice(nodes=children[:]) if len(children) > 1 else children[0]
        return retval

    def visit_operation(self, node, children):
        action_nodes = children[1]
        actions = []
        for action_node in action_nodes:
            action = []
            for i in range(len(action_node)):
                action.append(str(action_node[i]))
            actions.append(action)
        return MatchActions(children[0], actions)

    def visit_state(self, node, children):
        # Just ignoring the syntax nodes
        return node[1]

    def visit_full_expression(self, node, children):
        if len(children) == 2:
            retval = Not() if children[0] == NOT else And()
            if isinstance(children[1], list):
                retval.nodes = children[1]
            else:
                retval.nodes = [children[1]]
        else:
            # If there is no optional prefix reduce.
            retval = children[0]

        return retval

    def visit_calls(self, node, children):
        call_arguments = [arg for arg in node if arg.rule_name == 'call']
        return call_arguments

    def visit_expression_with_state(self, node, children):
        if len(children) == 1:
            return children[0]

        state_name = str(children[0])
        rule_node = children[1]
        retval = MatchState(rule_node, state_name)
        return retval


    def visit_repeated_expression(self, node, children):
        if len(children) == 1:
            return children[0]

        nodes = children[0] if isinstance(children[0], list) else [children[0]]
        if children[1] == ZERO_OR_MORE:
            retval = ZeroOrMore(nodes=nodes)
        elif children[1] == ONE_OR_MORE:
            retval = OneOrMore(nodes=nodes)
        elif children[1] == OPTIONAL:
            retval = Optional(nodes=nodes)
        else:
            retval = UnorderedGroup(nodes=nodes[0].nodes)

        return retval

    def visit_rule_crossref(self, node, children):
        return CrossRef(node.value)

    def visit_regex(self, node, children):
        match = _(node.value[2:-1], ignore_case=self.ignore_case)
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
            except UnicodeDecodeError as e:
                raise GrammarError(f"Invalid escape sequence '{match.group(0)}'.") from e
        match_str = PEG_ESCAPE_SEQUENCES_RE.sub(decode_escape, match_str)

        return StrMatch(match_str, ignore_case=self.ignore_case)


class ParserState:
    def __init__(self, parser):
        self._parser = parser


class ParserPEGState(ParserState):
    rule_reference_stack: dict
    rule_reference_set: dict
    states_stack: list

    def __init__(self, parser):
        super().__init__(parser)
        self.rule_reference_stack = {}
        self.rule_reference_set = {}
        self.states_stack = []


class ParserPEGActions:
    def __init__(self, parser):
        self._parser = parser

    def push(self, rule: Match, matched_result, c_pos, args=None):
        stack = self._parser.state.rule_reference_stack
        stack.setdefault(rule.rule_name, [])
        name = str(matched_result)
        stack[rule.rule_name].append(name)
        return matched_result

    def pop(self, rule: Match, matched_result, c_pos, args=None):
        stack = self._parser.state.rule_reference_stack
        if not stack.get(rule.rule_name):
            if self._parser.debug:
                self._parser.dprint(
                    f"-- The stack for `{rule.rule_name}` rule is empty at {c_pos} => "
                    f"'{self._parser.context(len(str(matched_result)))}'")
            self._parser._nm_raise(rule, c_pos, self._parser)

        match_against = stack[rule.rule_name][-1]

        matched_str = str(matched_result)
        if matched_str != match_against:
            if self._parser.debug:
                self._parser.dprint(
                    f"-- No match '{match_against}' at {c_pos} => "
                    f"'{self._parser.context(len(match_against))}'")
            self._parser._nm_raise(rule, c_pos, self._parser)
        stack[rule.rule_name].pop()
        return matched_result

    def pop_front(self, rule: Match, matched_result, c_pos, args=None):
        stack = self._parser.state.rule_reference_stack
        if not stack.get(rule.rule_name):
            if self._parser.debug:
                self._parser.dprint(
                    f"-- The stack for `{rule.rule_name}` rule is empty at {c_pos} => "
                    f"'{self._parser.context(len(str(matched_result)))}'")
            self._parser._nm_raise(rule, c_pos, self._parser)

        match_against = stack[rule.rule_name][0]

        matched_str = str(matched_result)
        if matched_str != match_against:
            if self._parser.debug:
                self._parser.dprint(
                    f"-- No match '{match_against}' at {c_pos} => "
                    f"'{self._parser.context(len(match_against))}'")
            self._parser._nm_raise(rule, c_pos, self._parser)
        stack[rule.rule_name].pop(0)
        return matched_result

    def add(self, rule: Match, matched_result, c_pos, args=None):
        reference_set = self._parser.state.rule_reference_set
        reference_set.setdefault(rule.rule_name, set())

        name = str(matched_result)
        reference_set[rule.rule_name].add(name)

        return matched_result

    def any(self, rule: Match, matched_result, c_pos, args=None):
        reference_set = self._parser.state.rule_reference_set
        if not reference_set.get(rule.rule_name):
            if self._parser.debug:
                self._parser.dprint(
                    f"-- The stack for `{rule.rule_name}` rule is empty at {c_pos} => "
                    f"'{self._parser.context(len(str(matched_result)))}'")
            self._parser._nm_raise(rule, c_pos, self._parser)

        rule_set = reference_set[rule.rule_name]

        matched_str = str(matched_result)
        if matched_str not in rule_set:
            if self._parser.debug:
                self._parser.dprint(
                    f"-- No known match for '{matched_str}' at {c_pos} => "
                    f"'{self._parser.context(len(matched_str))}'")
            self._parser._nm_raise(rule, c_pos, self._parser)

        return matched_result

    def state(self, rule: Match, matched_result, c_pos, args=None):
        if not args:
            if self._parser.debug:
                self._parser.dprint(
                    f"-- Not enough arguments for state action at {c_pos} => "
                    f"'{self._parser.context()}'")
            self._parser._nm_raise(rule, c_pos, self._parser)

        states_stack = self._parser.state.states_stack
        state_method = getattr(self, args[0] + '_state')
        return state_method(rule, matched_result, c_pos, args=args[1:] or None)

    def push_state(self, rule: Match, matched_result, c_pos, args=None):
        if not args:
            if self._parser.debug:
                self._parser.dprint(
                    f"-- Not enough arguments for state action at {c_pos} => "
                    f"'{self._parser.context()}'")
            self._parser._nm_raise(rule, c_pos, self._parser)

        states_stack = self._parser.state.states_stack
        state_name = args[0]
        states_stack.append(state_name)

        return matched_result

    def pop_state(self, rule: Match, matched_result, c_pos, args=None):
        states_stack = self._parser.state.states_stack
        state_name = args[0] if args else None
        if state_name:
            if state_name != states_stack[-1]:
                if self._parser.debug:
                    self._parser.dprint(
                        f"-- State `{states_stack[-1]}` doesn't match `{state_name}` state {c_pos} => "
                        f"'{self._parser.context()}'")
                self._parser._nm_raise(rule, c_pos, self._parser)

        states_stack.pop()

        return matched_result


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
        super().__init__(*args, **kwargs)

        self.state = ParserPEGState(self)
        self.actions = ParserPEGActions(self)

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
                self.parser_model, f"{root_rule}_peg_parser_model.dot")

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
