#######################################################################
# Name: peg.py
# Purpose: Implementing PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@ya.ru>
# Copyright: (c) 2009-2017 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2025 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>, Andrey N. Dotsenko <pgandrey@ya.ru>
# License: MIT License
#######################################################################
import abc
import codecs
import copy
import enum
import re
import typing
import collections.abc


from arpeggio import (
    EOF,
    And,
    CrossRef,
    EndOfFile,
    GrammarError,
    HistorySequencePush,
    HistorySequencePop,
    HistorySequencePopFront,
    HistorySetAdd,
    Not,
    OneOrMore,
    Optional,
    OrderedChoice,
    ParserState,
    ParserStateLayer,
    Parser,
    ParserPython,
    ParseTreeNode,
    PTNodeVisitor,
    SemanticError,
    Sequence,
    StrMatch,
    UnorderedGroup,
    ZeroOrMore,
    visit_parse_tree,
    ParsingExpression,
    ParsingStatement,
    MatchState,
    PushState,
    PopState,
    StateWrapper,
    ParsingState,
    ParserModelItem,
)
from arpeggio import RegExMatch as _

__all__ = ['ParserPEG']

# Lexical invariants
LEFT_ARROW = "<-"
ORDERED_CHOICE = "/"
ZERO_OR_MORE = "*"
ONE_OR_MORE_SYMBOL = '+'
ONE_OR_MORE = _('(?<!\\s)\\' + ONE_OR_MORE_SYMBOL)
OPTIONAL = "?"
UNORDERED_GROUP = "#"
AND = "&"
NOT = "!"
OPEN = "("
CLOSE = ")"
CALL_START = StrMatch("{", suppress=True)
CALL_END = StrMatch("}", suppress=True)
CALL_DELIMITER = StrMatch(',', suppress=True)
STATE = StrMatch('@', suppress=True)
PUSH_STATE = StrMatch('+@', suppress=True)
POP_STATE = StrMatch('-@', suppress=True)
STATE_LAYER_START = StrMatch('@(', suppress=True)
STATE_LAYER_END = StrMatch(')', suppress=True)


# PEG syntax rules
def peggrammar():
    return OneOrMore(rule), EOF


def rule():
    return rule_name, LEFT_ARROW, ordered_choice, ";"


def ordered_choice():
    return sequence, ZeroOrMore(ORDERED_CHOICE, sequence)


def sequence():
    return OneOrMore(full_expression)


def full_expression():
    return Optional([AND, NOT]), repeated_expression


def repeated_expression():
    return statement, Optional([
        OPTIONAL,
        ZERO_OR_MORE,
        ONE_OR_MORE,
        UNORDERED_GROUP
    ])


def statement():
    return [
        expression,
        parsing_state,
        push_parsing_state,
        pop_parsing_state,
    ]


def expression():
    return parsing_expression, Optional(action_calls)


def parsing_expression():
    return [
        regex,
        str_match,
        rule_crossref,
        (OPEN, ordered_choice, CLOSE),
        wrapped_with_state_layer,
    ]


def parsing_state():
    return STATE, parsing_state_name


def push_parsing_state():
    return PUSH_STATE, parsing_state_name


def pop_parsing_state():
    return POP_STATE, parsing_state_name


def parsing_state_name():
    return _(r'[a-zA-Z_][a-zA-Z_0-9]*')


def wrapped_with_state_layer():
    return (
        STATE_LAYER_START,
        ordered_choice,
        STATE_LAYER_END
    )


def action_calls():
    return CALL_START, action_call, ZeroOrMore((CALL_DELIMITER, action_call)), CALL_END


def action_call():
    return OneOrMore(action_call_argument)


def action_call_argument():
    return [_(r'\w+'), quoted_string]


def quoted_string():
    return _(r'''(?s)('[^'\\]*(?:\\.[^'\\]*)*')|'''
             r'''("[^"\\]*(?:\\.[^"\\]*)*")''')


# PEG Lexical rules
def regex():
    return _(r"""(r'[^'\\]*(?:\\.[^'\\]*)*')|"""
             r'''(r"[^"\\]*(?:\\.[^"\\]*)*")''')


def rule_name():
    return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")


def rule_crossref():
    return rule_name


def str_match():
    return quoted_string()


def comment():
    return _("//.*\n", multiline=False)


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


class StateLayerScope(enum.Enum):
    """
    An enumeration used to identify the stack layer that should be used in an expression.
    """
    GLOBAL = 0
    PARENT = -2
    CURRENT = -1


class MatchedAction:
    """
    An abstract class for all action classes used in MatchActions parsing rules.
    """
    _rule: ParsingExpression  # bounding to this type for the rule_name attribute
    _args: collections.abc.Sequence[typing.Any] | None

    def __init__(
        self,
        rule: ParsingExpression,
        args: collections.abc.Sequence[typing.Any] = None,
    ):
        self._rule = rule
        self._args = args

    @abc.abstractmethod
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        """
        This method must be implemented to run an action over the match result.

        Parameters:
        parser
            A parser used to parse the source code.
        matched_result
            The match result that need to be processed by the action.
        c_pos
            The parser position before the corresponding (the MatchActions child rule) rule was matched.
        args
            Additional arguments that were passed to the action.

        Returns:
            A match result (usually the same as matched_result).
        """
        pass

    def __str__(self):
        return f'{str(self._rule)}{{{' '.join(map(str, self._args))}}}'


class ActionPush(MatchedAction):
    """
    An action that is used to push a matched token onto the stack according to the rule name.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        parser.state.push_rule_reference(self._rule.rule_name, str(matched_result))
        return matched_result


class ActionPop(MatchedAction):
    """
    An action that is used to remove a matched token from the top of the matches list according to the rule name.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        matched_str = str(matched_result)
        try:
            removed = parser.state.pop_rule_reference(self._rule.rule_name, matched_str)
        except (IndexError, KeyError):
            if parser.debug:
                parser.dprint(
                    f"-- The stack for `{self._rule.rule_name}` rule is empty at {c_pos} => "
                    f"'{parser.context(len(str(matched_result)))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        if not removed:
            if parser.debug:
                match_against = parser.state.last_pushed_rule_reference(self._rule.rule_name)
                parser.dprint(
                    f"-- No match '{match_against}' at {c_pos} => "
                    f"'{parser.context(len(match_against))}'")
            parser._nm_raise(self._rule, c_pos, parser)
        return matched_result


class ActionListAppend(MatchedAction):
    """
    An action that is used to append the list of matched tokens with a matched token according to the rule name.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        if matched_result is None:
            matched_str = ''
        else:
            matched_str = str(matched_result)
        parser.state.append_rule_reference(self._rule.rule_name, matched_str)
        return matched_result


class ActionListLast(MatchedAction):
    """
    An action that is used to match the last matched token from the top of the matches list according to the rule name.
    """
    _state_scope: StateLayerScope = StateLayerScope.CURRENT

    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        if matched_result is None:
            matched_str = ''
        else:
            matched_str = str(matched_result)

        try:
            last = parser.state.last_rule_reference(self._rule.rule_name, self._state_scope)
        except (IndexError, KeyError):
            if parser.debug:
                parser.dprint(
                    f"-- The stack for `{self._rule.rule_name}` rule is empty at {c_pos} => "
                    f"'{parser.context(len(str(matched_result)))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        if matched_str != last:
            if parser.debug:
                parser.dprint(
                    f"-- No match '{last}' at {c_pos} => "
                    f"'{parser.context(len(last))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        return matched_result


class ActionTryRemoveLast(MatchedAction):
    """
    An action that is used to remove the last matched token from the list of matched tokens according to the rule name.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        parser.state.try_remove_last_rule_reference(self._rule.rule_name)
        return matched_result


class ActionParentListLast(ActionListLast):
    """
    An action that is used to match the last matched token from the top of the matches list of the parent's stack layer
    according to the rule name.
    """
    _state_scope: StateLayerScope = StateLayerScope.PARENT


class ActionLonger(MatchedAction):
    """
    An action that is used to match a longer token than the last matched token from the top of the matches list
    according to the rule name.
    """
    _state_scope: StateLayerScope = StateLayerScope.CURRENT

    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        matched_str = str(matched_result)
        try:
            last = parser.state.last_rule_reference(self._rule.rule_name, self._state_scope)
        except (IndexError, KeyError):
            if parser.debug:
                parser.dprint(
                    f"-- The stack for `{self._rule.rule_name}` rule is empty or parent stack doesn't exist at {c_pos} => "
                    f"'{parser.context(len(str(matched_result)))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        if len(matched_str) <= len(last):
            if parser.debug:
                parser.dprint(
                    f"-- Match '{matched_str}' is not longer than parent's '{last}' at {c_pos} => "
                    f"'{parser.context(len(matched_str))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        return matched_result


class ActionParentListLonger(ActionLonger):
    """
    An action that is used to match a longer token than the last matched token from the top of the matches list of
    the parent's stack layer according to the rule name.
    """
    _state_scope: StateLayerScope = StateLayerScope.PARENT


class ActionPopFront(MatchedAction):
    """
    An action that is used to remove a matched token from the bottom of the matches list according to the rule name.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        matched_str = str(matched_result)
        try:
            removed = parser.state.pop_front_rule_reference(self._rule.rule_name, matched_str)
        except (IndexError, KeyError):
            if parser.debug:
                parser.dprint(
                    f"-- The stack for `{self._rule.rule_name}` rule is empty at {c_pos} => "
                    f"'{parser.context(len(str(matched_result)))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        if not removed:
            if parser.debug:
                match_against = parser.state.first_pushed_rule_reference(self._rule.rule_name)
                parser.dprint(
                    f"-- No match '{match_against}' at {c_pos} => "
                    f"'{parser.context(len(match_against))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        return matched_result


class ActionAdd(MatchedAction):
    """
    An action that is used to add a matched token to the set of matched tokens.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        matched_str = str(matched_result)
        parser.state.remember_rule_reference(self._rule.rule_name, matched_str)
        return matched_result


class ActionParentAdd(MatchedAction):
    """
    An action that is used to add a matched token to the set of matched tokens of the parent state layer.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        matched_str = str(matched_result)
        parser.state.remember_rule_reference(
            self._rule.rule_name,
            matched_str,
            state_layer_scope = StateLayerScope.PARENT  # noqa: E251
        )
        return matched_result


class ActionGlobalAdd(MatchedAction):
    """
    An action that is used to add a matched token to the set of matched tokens of the global state layer.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        matched_str = str(matched_result)
        parser.state.remember_rule_reference(
            self._rule.rule_name,
            matched_str,
            state_layer_scope = StateLayerScope.GLOBAL  # noqa: E251
        )
        return matched_result


class ActionAny(MatchedAction):
    """
    An action that is used to check if the matched token was previously added to the set of the matched tokens.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        matched_str = str(matched_result)

        is_known = parser.state.rule_reference_is_known(self._rule.rule_name, matched_str)
        if not is_known:
            if parser.debug:
                parser.dprint(
                    f"-- No known match for '{matched_str}' at {c_pos} => "
                    f"'{parser.context(len(matched_str))}'")
            parser._nm_raise(self._rule, c_pos, parser)

        return matched_result


class ActionSuppress(MatchedAction):
    """
    An action that is used to suppress a rule.
    """
    @typing.override
    def run(
        self,
        parser: 'ParserPEG',
        matched_result: ParseTreeNode | None,
        c_pos: int,
        args: collections.abc.Sequence[typing.Any] = None,
    ) -> ParseTreeNode | None:
        return None


class MatchActions(ParsingExpression):
    """
    Apply some actions to a matched rule.

    This rule parses his child rule and then runs stored actions over the result. Each action except the first one
    receives the previous action result and returns its own result (usually the same).
    """
    actions: list[MatchedAction]

    def __init__(self, rule: ParsingStatement, actions: list[MatchedAction]):
        super().__init__(rule_name='', nodes=[rule])
        self.actions = actions

    @typing.override
    def _parse(self, parser: 'ParserPEG'):
        rule_node = self.nodes[0]
        c_pos = parser.position
        retval = rule_node.parse(parser)
        for action in self.actions:
            retval = action.run(parser, retval, c_pos)
        return retval

    def __str__(self):
        rule_node = self.nodes[0]
        return str(rule_node)

    @property
    def desc(self):
        return "{}{{{}}}{}".format(
            self.name,
            ', '.join(map(lambda x: ' '.join(str(x)), self.actions)),
            "-" if self.suppress else "",
        )

    @typing.override
    def resolve(
        self,
        resolve_cb: typing.Callable[[ParserModelItem], ParserModelItem]
    ) -> 'MatchActions':
        node = super().resolve(resolve_cb)
        for action in node.actions:
            action._rule = node.nodes[0]
        return node


class PEGVisitor(PTNodeVisitor):
    """
    Visitor that transforms parse tree to a PEG parser for the given language.
    """
    _parsing_state_by_name: dict[str, ParsingState]
    _last_parsing_state_id: int

    matched_actions: dict[str, type[MatchedAction]] = {
        'push': ActionPush,
        'pop': ActionPop,
        'pop_front': ActionPopFront,
        'add': ActionAdd,
        'any': ActionAny,
        'list_append': ActionListAppend,
        'list_try_remove': ActionTryRemoveLast,
        'list_last': ActionListLast,
        'list_longer': ActionLonger,
        'parent_add': ActionParentAdd,
        'global_add': ActionGlobalAdd,
        'suppress': ActionSuppress,
        'parent_list_last': ActionParentListLast,
        'parent_list_longer': ActionParentListLonger,
    }
    matched_actions_aliases: dict[str, dict[str, str]] = {
        'state': {
            'push': 'push_state',
            'pop': 'pop_state',
        },
        'parent': {
            'add': 'parent_add',
            'list': {
                'parent_last': 'list_parent_last',
                'longer': 'parent_list_longer',
                'last': 'parent_list_last',
            },
        },
        'global': {
            'add': 'global_add',
        },
        'list': {
            'append': 'list_append',
            'last': 'list_last',
            'try': {
                'remove': 'list_try_remove',
            },
        },
    }

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

        self._last_parsing_state_id = 0
        self._parsing_state_by_name = {}

    def register_parsing_state(self, state_name: str):
        self._last_parsing_state_id += 1
        parsing_state_id = self._last_parsing_state_id
        parsing_state = ParsingState(state_name, parsing_state_id)
        self._parsing_state_by_name[state_name] = parsing_state
        return parsing_state

    def get_state_by_name(self, state_name: str):
        parsing_state = self._parsing_state_by_name.get(state_name)
        if not parsing_state:
            parsing_state = self.register_parsing_state(state_name)
        return parsing_state

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
                return resolved_rule.resolve(_resolve)
            else:
                node.resolve(_resolve)
                self.resolved.add(node)
                return node

        # Find root and comment rules
        self.resolved = set()
        comment_rule = None
        for rule in children:
            if rule.rule_name == self.root_rule_name:
                root_rule = rule.resolve(_resolve)
            if rule.rule_name == self.comment_rule_name:
                comment_rule = rule.resolve(_resolve)

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

    def postprocess_action_args(self, args):
        action_name = args[0]

        if action_name in {'push_state', 'pop_state'}:
            state_name = args[1]
            parsing_state = self._parsing_state_by_name.get(state_name)
            if not parsing_state:
                parsing_state = self.register_parsing_state(state_name)
            args[1] = parsing_state

        return args

    def preprocess_action_args(self, args):
        if len(args) == 1:
            return args

        alias = self.matched_actions_aliases
        for i, arg in enumerate(args):
            alias = alias.get(arg)
            if type(alias) is str:
                del args[:i]
                args[0] = alias
            elif alias is None:
                return args

        return args

    def visit_expression(self, node, children):
        if len(children) == 1:
            return children[0]

        action_nodes = children[1]
        actions = []
        rule_node = children[0]
        for action_node in action_nodes:
            action_args = [str(action_node[i]) for i in range(len(action_node))]
            action_args = self.preprocess_action_args(action_args)
            action_args = self.postprocess_action_args(action_args)
            action_name = action_args[0]
            action = self.matched_actions[action_name](rule_node, action_args[1:])
            actions.append(action)
        return MatchActions(children[0], actions)

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

    def visit_action_calls(self, node, children):
        return children

    def visit_action_call(self, node, children):
        return children

    def visit_quoted_string(self, node, children):
        matched_str = str(node)
        return self.decode_escaped_str(matched_str[1:-1])

    def visit_parsing_state(self, node, children):
        state_name = str(node)
        parsing_state = self.get_state_by_name(state_name)
        return MatchState(parsing_state)

    def visit_push_parsing_state(self, node, children):
        state_name = str(node)
        parsing_state = self.get_state_by_name(state_name)
        return PushState(parsing_state)

    def visit_pop_parsing_state(self, node, children):
        state_name = str(node)
        parsing_state = self.get_state_by_name(state_name)
        return PopState(parsing_state)

    def visit_wrapped_with_state_layer(self, node, children):
        return StateWrapper(children[0])

    def visit_repeated_expression(self, node, children):
        if len(children) == 1:
            return children[0]

        nodes = children[0] if isinstance(children[0], list) else [children[0]]
        if children[1] == ZERO_OR_MORE:
            retval = ZeroOrMore(nodes=nodes)
        elif children[1] == ONE_OR_MORE_SYMBOL:
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

    def decode_escaped_str(self, s):
        # Scan the string literal, and sequentially match those escape
        # sequences which are syntactically valid Python. Attempt to convert
        # those, raising ``GrammarError`` for any semantically invalid ones.
        def decode_escape(match):
            try:
                return codecs.decode(match.group(0), "unicode_escape")
            except UnicodeDecodeError as e:
                raise GrammarError(f"Invalid escape sequence '{match.group(0)}'.") from e

        return PEG_ESCAPE_SEQUENCES_RE.sub(decode_escape, s)

    def visit_str_match(self, node, children):
        match_str = node.value[1:-1]
        match_str = self.decode_escaped_str(match_str)
        return StrMatch(match_str, ignore_case=self.ignore_case)


class ParserPEGStateLayer(ParserStateLayer):
    """
    A class that holds additional data used in PEG expressions.
    """
    rule_reference_stack: dict[str, str]
    rule_reference_set: dict[str, str]
    rule_reference_list: dict[str, str]

    def __init__(self):
        super().__init__()
        self.rule_reference_stack = {}
        self.rule_reference_set = {}
        self.rule_reference_list = {}

    def __deepcopy__(self, memo: dict = None):
        copied = super().__deepcopy__(memo)
        copied.rule_reference_stack = copy.deepcopy(self.rule_reference_stack, memo)
        copied.rule_reference_set = copy.deepcopy(self.rule_reference_set, memo)
        copied.rule_reference_list = copy.deepcopy(self.rule_reference_list, memo)
        return copied

    def __bool__(self):
        if super().__bool__():
            return True

        rule_reference_stack_is_empty = True
        for key, value in self.rule_reference_stack.items():
            if value:
                rule_reference_stack_is_empty = False

        rule_reference_set_is_empty = True
        for key, value in self.rule_reference_set.items():
            if value:
                rule_reference_set_is_empty = False

        rule_reference_list_is_empty = True
        for key, value in self.rule_reference_list.items():
            if value:
                rule_reference_list_is_empty = False

        if rule_reference_stack_is_empty and rule_reference_set_is_empty and rule_reference_list_is_empty:
            return False

        return True


    @typing.override
    def queues_are_empty(self) -> bool:
        if not super().queues_are_empty():
            return False

        rule_reference_stack_is_empty = True
        for key, value in self.rule_reference_stack.items():
            if value:
                rule_reference_stack_is_empty = False

        return rule_reference_stack_is_empty

    def __str__(self):
        return f"""{super().__str__()}
Rule references queue:
{str(self.rule_reference_stack)}
Known rule references:
{str(self.rule_reference_set)}
"""


class ParserPEGState(ParserState):
    """
    A class that manages additional data used in PEG expressions.
    """
    _state_layer_class: ParserStateLayer = ParserPEGStateLayer

    def __init__(self):
        super().__init__()

    def push_rule_reference(
        self,
        rule_name: str,
        reference_name: str,
    ):
        stack = self.state_layers[-1].rule_reference_stack.setdefault(rule_name, [])
        stack.append(reference_name)
        self._actions_history.append(HistorySequencePush(stack, reference_name))

    def pop_rule_reference(
        self,
        rule_name: str,
        expected_reference_name: str = None,
    ) -> str | None:
        stack = self.state_layers[-1].rule_reference_stack[rule_name]
        if expected_reference_name is not None and stack[-1] != expected_reference_name:
            return None
        reference_name = stack.pop()
        self._actions_history.append(HistorySequencePop(stack, reference_name))
        return reference_name

    def pop_front_rule_reference(
        self,
        rule_name: str,
        expected_reference_name: str = None,
    ) -> str | None:
        stack = self.state_layers[-1].rule_reference_stack[rule_name]
        if expected_reference_name is not None and stack[0] != expected_reference_name:
            return None
        reference_name = stack.pop(0)
        self._actions_history.append(HistorySequencePopFront(stack, reference_name))
        return reference_name

    def first_pushed_rule_reference(self, rule_name: str) -> str | None:
        stack = self.state_layers[-1].rule_reference_stack.get(rule_name)
        if not stack:
            return None
        return stack[0]

    def last_pushed_rule_reference(
        self,
        rule_name: str,
        state_layer_scope: StateLayerScope = StateLayerScope.CURRENT,
    ) -> str | None:
        layer_num = state_layer_scope.value
        stack = self.state_layers[layer_num].rule_reference_stack[rule_name]
        if not stack:
            return None
        return stack[-1]

    def append_rule_reference(
        self,
        rule_name: str,
        reference_name: str,
    ):
        stack = self.state_layers[-1].rule_reference_list.setdefault(rule_name, [])
        stack.append(reference_name)
        self._actions_history.append(HistorySequencePush(stack, reference_name))

    def try_remove_last_rule_reference(
        self,
        rule_name: str,
    ):
        stack = self.state_layers[-1].rule_reference_list.setdefault(rule_name, [])
        if not stack:
            return  # Was just trying.

        item = stack[-1]
        del stack[-1]
        self._actions_history.append(HistorySequencePop(stack, item))

    def last_rule_reference(
        self,
        rule_name: str,
        state_layer_scope: StateLayerScope = StateLayerScope.CURRENT,
    ) -> str | None:
        layer_num = state_layer_scope.value
        stack = self.state_layers[layer_num].rule_reference_list[rule_name]
        if not stack:
            return None
        return stack[-1]

    def remember_rule_reference(
        self,
        rule_name: str,
        reference_name: str,
        state_layer_scope: StateLayerScope = StateLayerScope.CURRENT
    ):
        layer_num = state_layer_scope.value
        reference_set = self.state_layers[layer_num].rule_reference_set.setdefault(rule_name, set())
        reference_set.add(reference_name)
        self._actions_history.append(HistorySetAdd(reference_set, reference_name))

    def known_rule_references(self, rule_name: str) -> set[str]:
        reference_set = self.state_layers[-1].rule_reference_set.get(rule_name)
        return reference_set

    def rule_reference_is_known(
        self,
        rule_name: str,
        reference_name: str
    ) -> bool:
        for state_layer in reversed(self.state_layers):
            reference_set = state_layer.rule_reference_set.get(rule_name)
            if reference_set is None:
                continue
            if reference_name in reference_set:
                return True
        return False


class ParserPEG(Parser):
    _state_class: type[ParserState] = ParserPEGState
    _state: _state_class

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

    # Override just to fix the hinting issue because it's not possible to override a field:
    @Parser.state.getter
    def state(self) -> _state_class:
        return self._state

    def _from_peg(self, language_def):
        parser = ParserPython(peggrammar, comment, reduce_tree=False,
                              debug=self.debug)
        parser.root_rule_name = self.root_rule_name
        parse_tree = parser.parse(language_def)

        return visit_parse_tree(parse_tree, PEGVisitor(self.root_rule_name,
                                                       self.comment_rule_name,
                                                       self.ignore_case,
                                                       debug=self.debug))
