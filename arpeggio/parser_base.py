# stdlib
import abc
import bisect
import codecs
import re
import types
from typing import Any, Dict, List

# proj
from . import arpeggio_settings
from . import peg_expressions
from . import peg_nodes
from . import peg_semantic_actions
from . import peg_utils


class Parser(peg_utils.DebugPrinter, abc.ABC):
    """
    Abstract base class for all parsers.

    Attributes:
        comments_model: parser model for comments.
        comments(list): A list of ParseTreeNode for matched comments.
        sem_actions(dict): A dictionary of semantic actions keyed by the
            rule name.
        parse_tree(NonTerminal): The parse tree consisting of NonTerminal and
            Terminal instances.
        in_rule (str): Current rule name.
        in_parse_comments (bool): True if parsing comments.
        in_lex_rule (bool): True if in lexical rule. Currently used in Combine
            decorator to convert match to a single Terminal.
        in_not (bool): True if in Not parsing expression. Used for better error
            reporting.
        last_pexpression (ParsingExpression): Last parsing expression
            traversed.
    """

    # Not marker for NoMatch rules list. Used if the first unsuccessful rule
    # match is Not.
    FIRST_NOT = peg_expressions.Not()

    def __init__(self, skipws: bool = True,
                 ws: str = arpeggio_settings.DEFAULT_WS,
                 reduce_tree: bool = False,
                 autokwd: bool = False,
                 ignore_case: bool = False,
                 memoization: bool = False, **kwargs):
        """
        Args:
            skipws (bool): Should the whitespace skipping be done.  Default is
                True.
            ws (str): A string consisting of whitespace characters.
            reduce_tree (bool): If true non-terminals with single child will be
                eliminated from the parse tree. Default is False.
            autokwd(bool): If keyword-like StrMatches are matched on word
                boundaries. Default is False.
            ignore_case(bool): If case is ignored (default=False)
            memoization(bool): If memoization should be used
                (a.k.a. packrat parsing)
        """

        super().__init__(**kwargs)  # init debug printer

        # Used to indicate state in which parser should not
        # treat newlines as whitespaces.
        self._eolterm = False

        self.skipws = skipws
        self.ws = ws
        self.reduce_tree = reduce_tree
        self.autokwd = autokwd
        self.ignore_case = ignore_case
        self.memoization = memoization
        self.comments_model = None
        self.comments: List[peg_nodes.ParseTreeNode] = []
        self.comment_positions: Dict[int, int] = dict()
        self.sem_actions: Dict[Any, Any] = dict()                           # Dict [rule_name] = Semantic Action  ToDo: narrow down typing
        self.parse_tree = None

        # Create regex used for autokwd matching
        flags = 0
        if ignore_case:
            flags = re.IGNORECASE
        self.keyword_regex = re.compile(r'[^\d\W]\w*', flags)

        # Keep track of root rule we are currently in.
        # Used for debugging purposes
        self.in_rule = ''

        self.in_parse_comments = False

        # Are we in lexical rule? If so do not
        # skip whitespaces.
        self.in_lex_rule = False

        # Are we in Not parsing expression?
        self.in_not = False

        # Last parsing expression traversed
        self.last_pexpression = None

    @property
    def ws(self):
        return self._ws

    @ws.setter
    def ws(self, new_value):
        self._real_ws = new_value
        self._ws = new_value
        if self.eolterm:
            self._ws = self._ws.replace('\n', '').replace('\r', '')

    @property
    def eolterm(self):
        return self._eolterm

    @eolterm.setter
    def eolterm(self, new_value):
        # Toggle newline char in ws on eolterm property set.
        # During eolterm state parser should not treat
        # newline as a whitespace.
        self._eolterm = new_value
        if self._eolterm:
            self._ws = self._ws.replace('\n', '').replace('\r', '')
        else:
            self._ws = self._real_ws

    @abc.abstractmethod
    def _parse(self):
        """ actual implementation of the parser"""
        pass

    def parse(self, _input: str, file_name=None):
        """
        Parses input and produces parse tree.

        Args:
            _input(str): An input string to parse.
            file_name(str): If input is loaded from file this can be
                set to file name. It is used in error messages.
        """
        self.position: int = 0      # Input position
        self.nm = None              # Last NoMatch exception
        self.line_ends: List[int] = list()
        self.input: str = _input
        self.file_name = file_name
        self.comment_positions = dict()
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        try:
            self.parse_tree = self._parse()
        except peg_expressions.NoMatch as e:
            # Remove Not marker
            if e.rules[0] is Parser.FIRST_NOT:
                del e.rules[0]
            # Get line and column from position
            e.line, e.col = self.pos_to_linecol(e.position)
            raise
        finally:
            # At end of parsing clear all memoization caches.
            # Do this here to free memory.
            if self.memoization:
                self._clear_caches()

        # In debug mode export parse tree to dot file for
        # visualization
        if self.debug and self.parse_tree:
            try:
                # imports for local pytest
                from .export import PTDOTExporter           # type: ignore # pragma: no cover
            except ImportError:                             # type: ignore # pragma: no cover
                # imports for doctest
                # noinspection PyUnresolvedReferences
                from export import PTDOTExporter            # type: ignore # pragma: no cover

            root_rule_name = self.parse_tree.rule_name
            PTDOTExporter().exportFile(
                self.parse_tree, "{}_parse_tree.dot".format(root_rule_name))
        return self.parse_tree

    def parse_file(self, file_name):
        """
        Parses content from the given file.
        Args:
            file_name(str): A file name.
        """
        with codecs.open(file_name, 'r', 'utf-8') as f:
            content = f.read()

        return self.parse(content, file_name=file_name)

    def getASG(self, sem_actions=None, defaults=True):
        """
        Creates Abstract Semantic Graph (ASG) from the parse tree.

        Args:
            sem_actions (dict): The semantic actions dictionary to use for
                semantic analysis. Rule names are the keys and semantic action
                objects are values.
            defaults (bool): If True a default semantic action will be
                applied in case no action is defined for the node.
        """
        if not self.parse_tree:
            raise Exception(
                "Parse tree is empty. You did call parse(), didn't you?")

        if sem_actions is None:
            if not self.sem_actions:
                raise Exception("Semantic actions not defined.")
            else:
                sem_actions = self.sem_actions

        if type(sem_actions) is not dict:
            raise Exception("Semantic actions parameter must be a dictionary.")

        for_second_pass = []

        def tree_walk(node):
            """
            Walking the parse tree and calling first_pass for every registered
            semantic actions and creating list of object that needs to be
            called in the second pass.
            """

            if self.debug:
                self.dprint(
                    "Walking down %s   type: %s  str: %s" %
                    (node.name, type(node).__name__, str(node)))

            children = peg_nodes.SemanticActionResults()
            if isinstance(node, peg_nodes.NonTerminal):
                for n in node:
                    child = tree_walk(n)
                    if child is not None:
                        children.append_result(n.rule_name, child)

            if self.debug:
                self.dprint("Processing %s = '%s'  type:%s len:%d" %
                            (node.name, str(node), type(node).__name__,
                             len(node) if isinstance(node, list) else 0))
                for i, a in enumerate(children):
                    self.dprint("  %d:%s type:%s" % (i + 1, str(a), type(a).__name__))

            if node.rule_name in sem_actions:
                sem_action = sem_actions[node.rule_name]
                if isinstance(sem_action, types.FunctionType):
                    retval = sem_action(self, node, children)
                else:
                    retval = sem_action.first_pass(self, node, children)

                if hasattr(sem_action, "second_pass"):
                    for_second_pass.append((node.rule_name, retval))

                if self.debug:
                    action_name = sem_action.__name__ \
                        if hasattr(sem_action, '__name__') \
                        else sem_action.__class__.__name__
                    self.dprint("  Applying semantic action %s" % action_name)

            else:
                if defaults:
                    # If no rule is present use some sane defaults
                    if self.debug:
                        self.dprint("  Applying default semantic action.")

                    retval = peg_semantic_actions.SemanticAction().first_pass(self, node, children)

                else:
                    retval = node

            if self.debug:
                if retval is None:
                    self.dprint("  Suppressed.")
                else:
                    self.dprint("  Resolved to = %s  type:%s" %
                                (str(retval), type(retval).__name__))
            return retval

        if self.debug:
            self.dprint("ASG: First pass")
        asg = tree_walk(self.parse_tree)

        # Second pass
        if self.debug:
            self.dprint("ASG: Second pass")
        for sa_name, asg_node in for_second_pass:
            sem_actions[sa_name].second_pass(self, asg_node)

        return asg

    def pos_to_linecol(self, pos):
        """
        Calculate (line, column) tuple for the given position in the stream.
        """
        if not self.line_ends:
            try:
                # TODO: Check this implementation on Windows.
                self.line_ends.append(self.input.index("\n"))
                while True:
                    try:
                        self.line_ends.append(
                            self.input.index("\n", self.line_ends[-1] + 1))
                    except ValueError:
                        break
            except ValueError:
                pass

        line = bisect.bisect_left(self.line_ends, pos)
        col = pos
        if line > 0:
            col -= self.line_ends[line - 1]
            if self.input[self.line_ends[line - 1]] in '\n\r':
                col -= 1
        return line + 1, col + 1

    def context(self, length=None, position=None):
        """
        Returns current context substring, i.e. the substring around current
        position.
        Args:
            length(int): If given used to mark with asterisk a length chars
                from the current position.
            position(int): The position in the input stream.
        """
        if not position:
            position = self.position
        if length:
            retval = "{}*{}*{}".format(
                str(self.input[max(position - 10, 0):position]),
                str(self.input[position:position + length]),
                str(self.input[position + length:position + 10]))
        else:
            retval = "{}*{}".format(
                str(self.input[max(position - 10, 0):position]),
                str(self.input[position:position + 10]))

        return retval.replace('\n', ' ').replace('\r', '')

    def _nm_raise(self, *args):
        """
        Register new NoMatch object if the input is consumed
        from the last NoMatch and raise last NoMatch.

        Args:
            args: A NoMatch instance or (value, position, parser)
        """

        rule, position, parser = args
        if self.nm is None or not parser.in_parse_comments:
            if self.nm is None or position > self.nm.position:
                if self.in_not:
                    self.nm = peg_expressions.NoMatch([Parser.FIRST_NOT], position, parser)
                else:
                    self.nm = peg_expressions.NoMatch([rule], position, parser)
            elif position == self.nm.position and isinstance(rule, peg_expressions.Match) \
                    and not self.in_not:
                self.nm.rules.append(rule)

        raise self.nm

    def _clear_caches(self):
        """ Clear memoization caches if packrat parser is used.
        """
        self.parser_model._clear_cache()
        if self.comments_model:
            self.comments_model._clear_cache()
