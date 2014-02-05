# -*- coding: utf-8 -*-
################################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This is an implementation of packrat parser interpreter based on PEG grammars.
# Grammars are defined using Python language constructs or the PEG textual
# notation.
################################################################################

import re
import bisect

DEFAULT_WS = '\t\n\r '


class ArpeggioError(Exception):
    """
    Base class for arpeggio errors.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
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


class NoMatch(Exception):
    """
    Exception raised by the Match classes during parsing to indicate that the
    match is not successful.

    Args:
        value (str): A name of the parsing expression or rule.
        position (int): A position in the input stream where exception occurred.
        parser (Parser): An instance of a parser.
    """
    def __init__(self, rule, position, parser):
        self.rule = rule
        self.position = position
        self.parser = parser

        # By default when NoMatch is thrown we will go up the Parser Model.
        self._up = True

    def __str__(self):
        return "Expected %s at position %s." % (self.rule,
                str(self.parser.pos_to_linecol(self.position)))


def flatten(_iterable):
    '''Flattening of python iterables.'''
    result = []
    for e in _iterable:
        if hasattr(e, "__iter__") and not type(e) in [str, NonTerminal]:
            result.extend(flatten(e))
        else:
            result.append(e)
    return result


# ---------------------------------------------------------
# Parser Model (PEG Abstract Semantic Graph) elements


class ParsingExpression(object):
    """
    An abstract class for all parsing expressions.
    Represents the node of the Parser Model.

    Attributes:
        elements: A list (or other python object) used as a staging structure
            for python based grammar definition. Used in _from_python for
            building nodes list of child parser expressions.
        rule (str): The name of the parser rule if this is the root rule.
        root (bool):  Does this parser expression represents the
            root of the parser rule? The root parser rule will create
            non-terminal node of the parse tree during parsing.
        nodes (list of ParsingExpression): A list of child parser expressions.
    """
    def __init__(self, *elements, **kwargs):

        if len(elements) == 1:
            elements = elements[0]
        self.elements = elements

        self.rule = kwargs.get('rule')
        self.root = kwargs.get('root', False)

        nodes = kwargs.get('nodes', [])
        if not hasattr(nodes, '__iter__'):
            nodes = [nodes]
        self.nodes = nodes

        # Memoization. Every node cache the parsing results for the given input
        # positions.
        self.result_cache = {}  # position -> parse tree

    @property
    def desc(self):
        return self.name

    @property
    def name(self):
        if self.root:
            return "%s(%s)" % (self.rule, self.__class__.__name__)
        else:
            return self.__class__.__name__

    @property
    def id(self):
        if self.root:
            return self.rule
        else:
            return id(self)

    def clear_cache(self, processed=None):
        """
        Clears memoization cache. Should be called on input change.

        Args:
            processed (set): Set of processed nodes to prevent infinite loops.
        """

        self.result_cache = {}
        if not processed:
            processed = set()

        for node in self.nodes:
            if node not in processed:
                processed.add(node)
                node.clear_cache(processed)

    def _parse_intro(self, parser):
        if parser.debug:
            print "Parsing %s" % self.name
        parser._skip_ws()
        self.c_pos = parser.position

    def parse(self, parser):
        self._parse_intro(parser)

        #Memoization.
        #If this position is already parsed by this parser expression than use
        #the result
        if self.c_pos in self.result_cache:
            if parser.debug:
                print "Result for [%s, %s] founded in result_cache." % \
                         (self, self.c_pos)
            result, new_pos = self.result_cache[self.c_pos]
            parser.position = new_pos
            return result

        # We are descending down
        if parser.nm:
            parser.nm._up = False

        result = self._parse(parser)

        if result:
            if parser.reduce_tree:
                if isinstance(result, list):
                    if self.root:
                        result = flatten(result)
                        if len(result) > 1:
                            result = NonTerminal(self.rule, self.c_pos, result)
                        else:
                            result = result[0]
            else:
                if self.root:
                    result = NonTerminal(self.rule, self.c_pos, result)

        # Result caching for use by memoization.
        self.result_cache[self.c_pos] = (result, parser.position)

        return result

    #TODO: _nm_change_rule should be called from every parser expression parse
    #         method that can potentialy be the root parser rule.
    def _nm_change_rule(self, nm, parser):
        """
        Change rule for the given NoMatch object to a more generic if
        we did not consume any input and we are moving up the parser model.
        Used to report most generic language element expected at the
        place of the NoMatch exception.
        """
        if self.root and self.c_pos == nm.position and nm._up:
            nm.rule = self.rule


class Sequence(ParsingExpression):
    """
    Will match sequence of parser expressions in exact order they are defined.
    """
    def _parse(self, parser):
        results = []
        try:
            for e in self.nodes:
                result = e.parse(parser)
                if result:
                    results.append(result)
        except NoMatch, m:
            self._nm_change_rule(m, parser)
            raise

        return results


class OrderedChoice(Sequence):
    """
    Will match one of the parser expressions specified. Parser will try to
    match expressions in the order they are defined.
    """
    def _parse(self, parser):
        result = None
        match = False
        for e in self.nodes:
            try:
                result = e.parse(parser)
                match = True
            except NoMatch, m:
                parser.position = self.c_pos  # Backtracking
                self._nm_change_rule(m, parser)
            else:
                break

        if not match:
            raise parser.nm

        return result


class Repetition(ParsingExpression):
    """
    Base class for all repetition-like parser expressions (?,*,+)
    """

class Optional(Repetition):
    """
    Optional will try to match parser expression specified buy will not fail in
    case match is not successful.
    """
    def _parse(self, parser):
        result = None
        try:
            result = self.nodes[0].parse(parser)
        except NoMatch:
            parser.position = self.c_pos  # Backtracking
            pass

        return result


class ZeroOrMore(Repetition):
    """
    ZeroOrMore will try to match parser expression specified zero or more
    times. It will never fail.
    """
    def _parse(self, parser):
        results = []
        while True:
            try:
                self.c_pos = parser.position
                results.append(self.nodes[0].parse(parser))
            except NoMatch:
                parser.position = self.c_pos  # Backtracking
                break

        return results


class OneOrMore(Repetition):
    """
    OneOrMore will try to match parser expression specified one or more times.
    """
    def _parse(self, parser):
        results = []
        first = False
        while True:
            try:
                self.c_pos = parser.position
                results.append(self.nodes[0].parse(parser))
                first = True
            except NoMatch:
                parser.position = self.c_pos  # Backtracking
                if not first:
                    raise
                break

        return results


class SyntaxPredicate(ParsingExpression):
    """
    Base class for all syntax predicates (and, not, empty).
    Predicates are parser expressions that will do the match but will not
    consume any input.
    """

class And(SyntaxPredicate):
    """
    This predicate will succeed if the specified expression matches current
    input.
    """
    def _parse(self, parser):
        for e in self.nodes:
            try:
                e.parse(parser)
            except NoMatch:
                parser.position = self.c_pos
                raise
        parser.position = self.c_pos


class Not(SyntaxPredicate):
    """
    This predicate will succeed if the specified expression doesn't match
    current input.
    """
    def _parse(self, parser):
        for e in self.nodes:
            try:
                e.parse(parser)
            except NoMatch:
                parser.position = self.c_pos
                return
        parser.position = self.c_pos
        parser._nm_raise(self.name, self.c_pos, parser)


class Empty(SyntaxPredicate):
    """
    This predicate will always succeed without consuming input.
    """
    def _parse(self, parser):
        pass


class Match(ParsingExpression):
    """
    Base class for all classes that will try to match something from the input.
    """
    def __init__(self, rule, root=False):
        super(Match, self).__init__(rule, root)

    @property
    def name(self):
        return "%s(%s)" % (self.__class__.__name__, self.to_match)

    def parse(self, parser):
        self._parse_intro(parser)
        if parser._in_parse_comment:
            return self._parse(parser)
        comments = []
        try:
            match = self._parse(parser)
        except NoMatch, nm:
            # If not matched try to match comment
            #TODO: Comment handling refactoring. Should think of better way to
            # handle comments.
            if parser.comments_model:
                try:
                    parser._in_parse_comment = True
                    while True:
                        comments.append(parser.comments_model.parse(parser))
                        parser._skip_ws()
                except NoMatch:
                    # If comment match successfull try terminal match again
                    if comments:
                        match = self._parse(parser)
                        match.comments = NonTerminal('comment', self.c_pos,
                                                     comments)
                    else:
                        parser._nm_raise(nm)
                finally:
                    parser._in_parse_comment = False

            else:
                parser._nm_raise(nm)

        return match


class RegExMatch(Match):
    '''
    This Match class will perform input matching based on Regular Expressions.

    Args:
        to_match (regex string): A regular expression string to match. It will be
            used to create regular expression using re.compile.
    '''
    def __init__(self, to_match, rule=None, flags=None):
        super(RegExMatch, self).__init__(rule)
        self.to_match = to_match
        if flags is not None:
            self.regex = re.compile(to_match, flags)
        else:
            self.regex = re.compile(to_match)

    def _parse(self, parser):
        m = self.regex.match(parser.input[parser.position:])
        if m:
            parser.position += len(m.group())
            if parser.debug:
                print "Match %s at %d" % (m.group(), self.c_pos)
            return Terminal(self.rule if self.root else '', self.c_pos,
                            m.group())
        else:
            if parser.debug:
                print "NoMatch at %d" % self.c_pos
            parser._nm_raise(self.root if self.root else self.name, self.c_pos,
                             parser)


class StrMatch(Match):
    """
    This Match class will perform input matching by a string comparison.

    Args:
        to_match (str): A string to match.
    """
    def __init__(self, to_match, rule=None, root=False):
        super(StrMatch, self).__init__(rule, root)
        self.to_match = to_match

    def _parse(self, parser):
        if parser.input[parser.position:].startswith(self.to_match):
            parser.position += len(self.to_match)
            if parser.debug:
                print "Match %s at %d" % (self.to_match, self.c_pos)
            return Terminal(self.rule if self.root else '', self.c_pos,
                            self.to_match)
        else:
            if parser.debug:
                print "NoMatch at %d" % self.c_pos
            parser._nm_raise(self.to_match, self.c_pos, parser)

    def __str__(self):
        return self.to_match

    def __eq__(self, other):
        return self.to_match == str(other)


# HACK: Kwd class is a bit hackish. Need to find a better way to
#	introduce different classes of string tokens.
class Kwd(StrMatch):
    """
    A specialization of StrMatch to specify keywords of the language.
    """
    def __init__(self, to_match):
        super(Kwd, self).__init__(to_match, rule=None)
        self.to_match = to_match
        self.root = True
        self.rule = 'keyword'


class EndOfFile(Match):
    """
    The Match class that will succeed in case end of input is reached.
    """
    def __init__(self, rule=None):
        super(EndOfFile, self).__init__(rule)

    @property
    def name(self):
        return "EOF"

    def _parse(self, parser):
        if len(parser.input) == parser.position:
            return Terminal(self.rule if self.root else '', self.c_pos, 'EOF')
        else:
            if parser.debug:
                print "EOF not matched."
            parser._nm_raise(self.name, self.c_pos, parser)


def EOF():      return EndOfFile()

# ---------------------------------------------------------


#---------------------------------------------------
# Parse Tree node classes

class ParseTreeNode(object):
    """
    Abstract base class representing node of the Parse Tree.
    The node can be terminal(the leaf of the parse tree) or non-terminal.

    Attributes:
        type (str): The name of the rule that created this node or empty
            string in case this node is created by a non-root pexpression.
        position (int): A position in the input stream where the match occurred.
        error (bool): Is this a false parse tree node created during error recovery.
        comments : A parse tree of comment(s) attached to this node.
    """
    def __init__(self, type, position, error):
        self.type = type
        self.position = position
        self.error = error
        self.comments = None

    @property
    def name(self):
        return "%s [%s]" % (self.type, self.position)


class Terminal(ParseTreeNode):
    """
    Leaf node of the Parse Tree. Represents matched string.

    Attributes:
        value (str): Matched string at the given position or missing token
            name in the case of an error node.
    """
    def __init__(self, type, position, value, error=False):
        super(Terminal, self).__init__(type, position, error)
        self.value = value

    @property
    def desc(self):
        return "%s '%s' [%s]" % (self.type, self.value, self.position)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return str(self) == str(other)


class NonTerminal(ParseTreeNode):
    """
    Non-leaf node of the Parse Tree. Represents language syntax construction.

    Attributes:
        nodes (list of ParseTreeNode): Children parse tree nodes.

    """
    def __init__(self, type, position, nodes, error=False):
        super(NonTerminal, self).__init__(type, position, error)
        self.nodes = flatten([nodes])

    @property
    def desc(self):
        return self.name

    def __iter__(self):
        return iter(self.nodes)

    def __str__(self):
        return "[ %s ]" % ", ".join([str(x) for x in self.nodes])


# ----------------------------------------------------
# Semantic Actions
#

class SemanticAction(object):
    """
    Semantic actions are executed during semantic analysis. They are in charge
    of producing Abstract Semantic Graph (ASG) out of the parse tree.
    Every non-terminal and terminal can have semantic action defined which will
    be triggered during semantic analysis.
    Semantic action triggering is separated in two passes. first_pass method is
    required and the method called second_pass is optional and will be called
    if exists after the first pass. Second pass can be used for forward
    referencing, e.g. linking to the declaration registered in the first pass
    stage.
    """
    def first_pass(self, parser, node, nodes):
        """
        Called in the first pass of tree walk.
        """
        raise NotImplementedError()


# ----------------------------------------------------
# Parsers


class Parser(object):
    """
    Abstract base class for all parsers.

    Attributes:
        skipws (bool): Should the whitespace skipping be done.
        ws (str): A string consisting of whitespace characters.
        reduce_tree (bool): If true non-terminals with single child will be
            eliminated from the parse tree.
        debug (bool): If true debugging messages will be printed.
        comments_model: parser model for comments.
    """
    def __init__(self, skipws=True, ws=DEFAULT_WS, reduce_tree=False, debug=False):
        self.skipws = skipws
        self.ws = ws
        self.reduce_tree = reduce_tree
        self.debug = debug
        self.comments_model = None
        self.sem_actions = {}

        self.parse_tree = None
        self._in_parse_comment = False

    def parse(self, _input):
        self.position = 0  # Input position
        self.nm = None  # Last NoMatch exception
        self.line_ends = []
        self.input = _input
        self.parser_model.clear_cache()
        self.parse_tree = self._parse()
        return self.parse_tree

    def getASG(self, sem_actions=None):
        """
        Creates Abstract Semantic Graph (ASG) from the parse tree.

        Args:
            sem_actions (dict): The semantic actions dictionary to use for semantic
                analysis. Rule names are the keys and semantic action objects are
                values.
        """
        if not self.parse_tree:
            raise Exception("Parse tree is empty. You did call parse(), didn't you?")

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
            nodes = []
            if isinstance(node, NonTerminal):
                for n in node.nodes:
                    nodes.append(tree_walk(n))

            if node.type in sem_actions:
                retval = sem_actions[node.type].first_pass(self, node, nodes)
                if hasattr(sem_actions[node.type], "second_pass"):
                    for_second_pass.append((node.type, retval))
            else:
                if isinstance(node, NonTerminal):
                    retval = NonTerminal(node.type, node.position, nodes)
                else:
                    retval = node

            return retval

        if self.debug:
            print "ASG: First pass"
        asg = tree_walk(self.parse_tree)

        # Second pass
        if self.debug:
            print "ASG: Second pass"
        for sa_name, asg_node in for_second_pass:
            sem_actions[sa_name].second_pass(self, asg_node)

        return asg

    def pos_to_linecol(self, pos):
        """
        Calculate (line, column) tuple for the given position in the stream.
        """
        if not self.line_ends:
            try:
                #TODO: Check this implementation on Windows.
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

    def _skip_ws(self):
        """
        Skiping whitespace characters.
        """
        if self.skipws:
            while self.position < len(self.input) and \
                    self.input[self.position] in self.ws:
                self.position += 1

    def _skip_comments(self):
        # We do not want to recurse into parsing comments
        if self.comments_model and not self.in_skip_comments:
            self.in_skip_comments = True
            comments = self.comments_model.parse(self)
            self.in_skip_comments = False
            return comments

    def _nm_raise(self, *args):
        """
        Register new NoMatch object if the input is consumed
        from the last NoMatch and raise last NoMatch.

        Args:
            args: A NoMatch instance or (value, position, parser)
        """
        if not self._in_parse_comment:
            if len(args) == 1 and isinstance(args[0], NoMatch):
                if self.nm is None or args[0].position > self.nm.position:
                    self.nm = args[0]
            else:
                value, position, parser = args
                if self.nm is None or position > self.nm.position:
                    self.nm = NoMatch(value, position, parser)
        raise self.nm


class ParserPython(Parser):
    def __init__(self, language_def, comment_def=None, *args, **kwargs):
        super(ParserPython, self).__init__(*args, **kwargs)

        # PEG Abstract Syntax Graph
        self.parser_model = self._from_python(language_def)
        self.comments_model = self._from_python(comment_def) \
            if comment_def else None

        # Comments should be optional and there can be more of them
        if self.comments_model:  # and not isinstance(self.comments_model, ZeroOrMore):
            self.comments_model.root = True
            self.comments_model.rule = comment_def.__name__

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

        class CrossRef(object):
            def __init__(self, rule_name):
                self.rule_name = rule_name

        def inner_from_python(expression):
            retval = None
            if callable(expression):  # Is this expression a parser rule?
                rule = expression.__name__
                if rule in __rule_cache:
                    c_rule = __rule_cache.get(rule)
                    if self.debug:
                        print "Rule %s founded in cache." % rule
                    if isinstance(c_rule, CrossRef):
                        self.__cross_refs += 1
                        if self.debug:
                            print "CrossRef usage: %s" % c_rule.rule_name
                    return c_rule

                # Semantic action for the rule
                if hasattr(expression, "sem"):
                    self.sem_actions[rule] = expression.sem

                # Register rule cross-ref to support recursion
                __rule_cache[rule] = CrossRef(rule)

                retval = inner_from_python(expression())
                retval.rule = rule
                retval.root = True

                # Update cache
                __rule_cache[rule] = retval
                if self.debug:
                    print "New rule: %s -> %s" % \
                          (rule, retval.__class__.__name__)

            elif isinstance(expression, Match):
                retval = expression

            elif isinstance(expression, Repetition) or \
                    isinstance(expression, SyntaxPredicate):
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

            elif type(expression) is str:
                retval = StrMatch(expression)

            else:
                raise GrammarError("Unrecognized grammar element '%s'." %
                                   str(expression))

            return retval

        # Cross-ref resolving
        def resolve():
            for e in __for_resolving:
                for i, node in enumerate(e.nodes):
                    if isinstance(node, CrossRef):
                        self.__cross_refs -= 1
                        e.nodes[i] = __rule_cache[node.rule_name]

        parser_model = inner_from_python(expression)
        resolve()
        assert self.__cross_refs == 0, "Not all crossrefs are resolved!"
        return parser_model

    def errors(self):
        pass
