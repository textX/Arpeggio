###############################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2019 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This is an implementation of packrat parser interpreter based on PEG
# grammars. Grammars are defined using Python language constructs or the PEG
# textual notation.
###############################################################################

# stdlib
import bisect
import codecs
import sys
import types

# proj
try:
    # imports for local pytest
    from .peg_expressions import *              # type: ignore # pragma: no cover
    from .peg_nodes import *                    # type: ignore # pragma: no cover
    from .peg_semantic_actions import *         # type: ignore # pragma: no cover

except ImportError:                             # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from peg_expressions import *               # type: ignore # pragma: no cover
    from peg_nodes import *                     # type: ignore # pragma: no cover
    from peg_semantic_actions import *          # type: ignore # pragma: no cover


__version__ = "1.9.2"

if sys.version < '3':
    raise RuntimeError('Python 3.x required')

DEFAULT_WS = '\t\n\r '


class ArpeggioError(Exception):
    """
    Base class for arpeggio errors.
    """
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)


class GrammarError(ArpeggioError):
    """
    Error raised during parser building phase used to indicate error in the
    grammar definition.
    """


class SemanticError(ArpeggioError):
    """
    Error raised during the phase of semantic analysis used to indicate
    semantic error.
    """


class DebugPrinter(object):
    """
    Mixin class for adding debug print support.

    Attributes:
        debug (bool): If true debugging messages will be printed.
        _current_ident(int): Current indention level for prints.
    """

    def __init__(self, **kwargs) -> None:

        self.debug = kwargs.pop("debug", False)
        self.file = kwargs.pop("file", sys.stdout)
        self._current_ident = 0

    def dprint(self, message, ident_change=0):
        """
        Handle debug message. Print to the stream specified by the 'file'
        keyword argument at the current indentation level. Default stream is
        stdout.
        """
        if ident_change < 0:
            self._current_ident += ident_change

        print(("%s%s" % ("   " * self._current_ident, message)),
              file=self.file)

        if ident_change > 0:
            self._current_ident += ident_change


# ----------------------------------------------------
# Semantic Actions
#
class PTNodeVisitor(DebugPrinter):
    """
    Base class for all parse tree visitors.
    """
    def __init__(self, defaults=True, **kwargs):
        """
        Args:
            defaults(bool): If the default visit method should be applied in
                case no method is defined.
        """
        self.for_second_pass = []
        self.defaults = defaults

        super(PTNodeVisitor, self).__init__(**kwargs)

    def visit__default__(self, node, children):
        """
        Called if no visit method is defined for the node.

        Args:
            node(ParseTreeNode):
            children(processed children ParseTreeNode-s):
        """
        if isinstance(node, Terminal):
            # Default for Terminal is to convert to string unless suppress flag
            # is set in which case it is suppressed by setting to None.
            retval = str(node) if not node.suppress else None
        else:
            retval = node
            # Special case. If only one child exist return it.
            if len(children) == 1:
                retval = children[0]
            else:
                # If there is only one non-string child return
                # that by default. This will support e.g. bracket
                # removals.
                last_non_str = None
                for c in children:
                    if not isinstance(c, str):
                        if last_non_str is None:
                            last_non_str = c
                        else:
                            # If there is multiple non-string objects
                            # by default convert non-terminal to string
                            if self.debug:
                                self.dprint("*** Warning: Multiple "
                                            "non-string objects found in "
                                            "default visit. Converting non-"
                                            "terminal to a string.")
                            retval = str(node)
                            break
                else:
                    # Return the only non-string child
                    retval = last_non_str

        return retval


def visit_parse_tree(parse_tree, visitor):
    """
    Applies visitor to parse_tree and runs the second pass
    afterwards.

    Args:
        parse_tree(ParseTreeNode):
        visitor(PTNodeVisitor):
    """
    if not parse_tree:
        raise Exception(
            "Parse tree is empty. You did call parse(), didn't you?")

    if visitor.debug:
        visitor.dprint("ASG: First pass")

    # Visit tree.
    result = parse_tree.visit(visitor)

    # Second pass
    if visitor.debug:
        visitor.dprint("ASG: Second pass")
    for sa_name, asg_node in visitor.for_second_pass:
        getattr(visitor, "second_%s" % sa_name)(asg_node)

    return result

# ----------------------------------------------------
# Parsers


class Parser(DebugPrinter):
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
    FIRST_NOT = Not()

    def __init__(self, skipws=True, ws=None, reduce_tree=False, autokwd=False,
                 ignore_case=False, memoization=False, **kwargs):
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

        super().__init__(**kwargs)

        # Used to indicate state in which parser should not
        # treat newlines as whitespaces.
        self._eolterm = False

        self.skipws = skipws
        if ws is not None:
            self.ws = ws
        else:
            self.ws = DEFAULT_WS

        self.reduce_tree = reduce_tree
        self.autokwd = autokwd
        self.ignore_case = ignore_case
        self.memoization = memoization
        self.comments_model = None
        self.comments = []
        self.comment_positions = {}
        self.sem_actions = {}

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

    def parse(self, _input, file_name=None):
        """
        Parses input and produces parse tree.

        Args:
            _input(str): An input string to parse.
            file_name(str): If input is loaded from file this can be
                set to file name. It is used in error messages.
        """
        self.position = 0  # Input position
        self.nm = None  # Last NoMatch exception
        self.line_ends = []
        self.input = _input
        self.file_name = file_name
        self.comment_positions = {}
        self.cache_hits = 0
        self.cache_misses = 0
        try:
            self.parse_tree = self._parse()
        except NoMatch as e:
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

            children = SemanticActionResults()
            if isinstance(node, NonTerminal):
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

                    retval = SemanticAction().first_pass(self, node, children)

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
                    self.nm = NoMatch([Parser.FIRST_NOT], position, parser)
                else:
                    self.nm = NoMatch([rule], position, parser)
            elif position == self.nm.position and isinstance(rule, Match) \
                    and not self.in_not:
                self.nm.rules.append(rule)

        raise self.nm

    def _clear_caches(self):
        """ Clear memoization caches if packrat parser is used.
        """
        self.parser_model._clear_cache()
        if self.comments_model:
            self.comments_model._clear_cache()


class CrossRef(object):
    """ Used for rule reference resolving.
    """
    def __init__(self, target_rule_name, position=-1):
        self.target_rule_name = target_rule_name
        self.position = position


class ParserPython(Parser):

    def __init__(self, language_def, comment_def=None, *args, **kwargs):
        """
        Constructs parser from python statements and expressions.

        Args:
            language_def (python function): A python function that defines
                the root rule of the grammar.
            comment_def (python function): A python function that defines
                the root rule of the comments grammar.
        """
        super().__init__(*args, **kwargs)

        # PEG Abstract Syntax Graph
        self.parser_model = self._from_python(language_def)

        self.comments_model = None
        if comment_def:
            self.comments_model = self._from_python(comment_def)
            self.comments_model.root = True
            self.comments_model.rule_name = comment_def.__name__

        # In debug mode export parser model to dot for
        # visualization
        if self.debug:
            try:
                # for Pytest
                from .export import PMDOTExporter
            except ImportError:
                # for local Doctest
                from export import PMDOTExporter

            root_rule = language_def.__name__
            PMDOTExporter().exportFile(self.parser_model,
                                       "{}_parser_model.dot".format(root_rule))

    def _parse(self):
        return self.parser_model.parse(self)

    def _from_python(self, expression):
        """
        Create parser model from the definition given in the form of python
        functions returning lists, tuples, callables, strings and
        ParsingExpression objects.

        Returns:
            Parser Model (PEG Abstract Semantic Graph)
        """
        __rule_cache = {"EndOfFile": EndOfFile()}
        __for_resolving = []  # Expressions that needs crossref resolvnih
        self.__cross_refs = 0

        def inner_from_python(expression):
            retval = None
            if isinstance(expression, types.FunctionType):
                # If this expression is a parser rule
                rule_name = expression.__name__
                if rule_name in __rule_cache:
                    c_rule = __rule_cache.get(rule_name)
                    if self.debug:
                        self.dprint("Rule {} founded in cache."
                                    .format(rule_name))
                    if isinstance(c_rule, CrossRef):
                        self.__cross_refs += 1
                        if self.debug:
                            self.dprint("CrossRef usage: {}"
                                        .format(c_rule.target_rule_name))
                    return c_rule

                # Semantic action for the rule
                if hasattr(expression, "sem"):
                    self.sem_actions[rule_name] = expression.sem

                # Register rule cross-ref to support recursion
                __rule_cache[rule_name] = CrossRef(rule_name)

                curr_expr = expression
                while isinstance(curr_expr, types.FunctionType):
                    # If function directly returns another function
                    # go into until non-function is returned.
                    curr_expr = curr_expr()
                retval = inner_from_python(curr_expr)
                retval.rule_name = rule_name
                retval.root = True

                # Update cache
                __rule_cache[rule_name] = retval
                if self.debug:
                    self.dprint("New rule: {} -> {}"
                                .format(rule_name, retval.__class__.__name__))

            elif type(expression) is str or isinstance(expression, StrMatch):
                if type(expression) is str:
                    retval = StrMatch(expression, ignore_case=self.ignore_case)
                else:
                    retval = expression
                    if expression.ignore_case is None:
                        expression.ignore_case = self.ignore_case

                if self.autokwd:
                    to_match = retval.to_match
                    match = self.keyword_regex.match(to_match)
                    if match and match.span() == (0, len(to_match)):
                        retval = RegExMatch(r'{}\b'.format(to_match),
                                            ignore_case=self.ignore_case,
                                            str_repr=to_match)
                        retval.compile()

            elif isinstance(expression, RegExMatch):
                # Regular expression are not compiled yet
                # to support global settings propagation from
                # parser.
                if expression.ignore_case is None:
                    expression.ignore_case = self.ignore_case
                expression.compile()

                retval = expression

            elif isinstance(expression, Match):
                retval = expression

            elif isinstance(expression, UnorderedGroup):
                retval = expression
                for n in retval.elements:
                    retval.nodes.append(inner_from_python(n))
                if any((isinstance(x, CrossRef) for x in retval.nodes)):
                    __for_resolving.append(retval)

            elif isinstance(expression, Sequence) or \
                    isinstance(expression, Repetition) or \
                    isinstance(expression, SyntaxPredicate) or \
                    isinstance(expression, Decorator):
                retval = expression
                retval.nodes.append(inner_from_python(retval.elements))
                if any((isinstance(x, CrossRef) for x in retval.nodes)):
                    __for_resolving.append(retval)

            elif type(expression) in [list, tuple]:
                if type(expression) is list:
                    retval = OrderedChoice(expression)
                else:
                    retval = Sequence(expression)

                retval.nodes = [inner_from_python(e) for e in expression]
                if any((isinstance(x, CrossRef) for x in retval.nodes)):
                    __for_resolving.append(retval)

            else:
                raise GrammarError("Unrecognized grammar element '%s'." %
                                   str(expression))

            # Translate separator expression.
            if isinstance(expression, Repetition) and expression.sep:
                expression.sep = inner_from_python(expression.sep)

            return retval

        # Cross-ref resolving
        def resolve():
            for e in __for_resolving:
                for i, node in enumerate(e.nodes):
                    if isinstance(node, CrossRef):
                        self.__cross_refs -= 1
                        e.nodes[i] = __rule_cache[node.target_rule_name]

        parser_model = inner_from_python(expression)
        resolve()
        assert self.__cross_refs == 0, "Not all crossrefs are resolved!"
        return parser_model

    def errors(self):
        pass
