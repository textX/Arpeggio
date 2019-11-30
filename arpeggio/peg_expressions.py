# Parser Model (PEG Abstract Semantic Graph) elements

# stdlib
import re
from typing import List

# proj
try:
    # imports for local pytest
    from .peg_nodes import *                    # type: ignore # pragma: no cover

except ImportError:                             # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from peg_nodes import *                     # type: ignore # pragma: no cover


NOMATCH_MARKER = 0


class ParsingExpression(object):
    """
    An abstract class for all parsing expressions.
    Represents the node of the Parser Model.

    Attributes:
        elements: A list (or other python object) used as a staging structure
            for python based grammar definition. Used in _from_python for
            building nodes list of child parser expressions.
        rule_name (str): The name of the parser rule if this is the root rule.
        root (bool):  Does this parser expression represents the
            root of the parser rule? The root parser rule will create
            non-terminal node of the parse tree during parsing.
        nodes (list of ParsingExpression): A list of child parser expressions.
        suppress (bool): If this is set to True than no ParseTreeNode will be
            created for this ParsingExpression. Default False.
    """
    def __init__(self, *elements, **kwargs):

        if len(elements) == 1:
            elements = elements[0]
        self.elements = elements

        self.rule_name = kwargs.get('rule_name', '')
        self.root = kwargs.get('root', False)

        nodes = kwargs.get('nodes', [])
        if not hasattr(nodes, '__iter__'):
            nodes = [nodes]
        self.nodes = nodes

        self.suppress = kwargs.get('suppress', False)

        # Memoization. Every node cache the parsing results for the given input
        # positions.
        self._result_cache = {}  # position -> parse tree at the position

    @property
    def desc(self):
        return "{}{}".format(self.name, "-" if self.suppress else "")

    @property
    def name(self):
        if self.root:
            return "%s=%s" % (self.rule_name, self.__class__.__name__)
        else:
            return self.__class__.__name__

    @property
    def id(self):
        if self.root:
            return self.rule_name
        else:
            return id(self)

    def _clear_cache(self, processed=None):
        """
        Clears memoization cache. Should be called on input change and end
        of parsing.

        Args:
            processed (set): Set of processed nodes to prevent infinite loops.
        """

        self._result_cache = {}

        if not processed:
            processed = set()

        for node in self.nodes:
            if node not in processed:
                processed.add(node)
                node._clear_cache(processed)

    def parse(self, parser):

        if parser.debug:
            name = self.name
            if name.startswith('__asgn'):
                name = "{}[{}]".format(self.name, self._attr_name)
            parser.dprint(">> Matching rule {}{} at position {} => {}"
                          .format(name,
                                  " in {}".format(parser.in_rule)
                                  if parser.in_rule else "",
                                  parser.position,
                                  parser.context()), 1)

        # Current position could change in recursive calls
        # so save it.
        c_pos = parser.position

        # Memoization.
        # If this position is already parsed by this parser expression use
        # the result
        if parser.memoization:
            try:
                result, new_pos = self._result_cache[c_pos]
                parser.position = new_pos
                parser.cache_hits += 1
                if parser.debug:
                    parser.dprint(
                        "** Cache hit for [{}, {}] = '{}' : new_pos={}"
                        .format(name, c_pos, str(result), str(new_pos)))
                    parser.dprint(
                        "<<+ Matched rule {} at position {}"
                        .format(name, new_pos), -1)

                # If NoMatch is recorded at this position raise.
                if result is NOMATCH_MARKER:
                    raise parser.nm

                # else return cached result
                return result

            except KeyError:
                parser.cache_misses += 1

        # Remember last parsing expression and set this as
        # the new last.
        last_pexpression = parser.last_pexpression
        parser.last_pexpression = self

        if self.rule_name:
            # If we are entering root rule
            # remember previous root rule name and set
            # this one on the parser to be available for
            # debugging messages
            previous_root_rule_name = parser.in_rule
            parser.in_rule = self.rule_name

        try:
            result = self._parse(parser)
            if self.suppress or (type(result) is list and result and result[0] is None):
                result = None

        except NoMatch:
            parser.position = c_pos  # Backtracking
            # Memoize NoMatch at this position for this rule
            if parser.memoization:
                self._result_cache[c_pos] = (NOMATCH_MARKER, c_pos)
            raise

        finally:
            # Recover last parsing expression.
            parser.last_pexpression = last_pexpression

            if parser.debug:
                parser.dprint("<<{} rule {}{} at position {} => {}"
                              .format("- Not matched"
                                      if parser.position is c_pos
                                      else "+ Matched",
                                      name,
                                      " in {}".format(parser.in_rule)
                                      if parser.in_rule else "",
                                      parser.position,
                                      parser.context()), -1)

            # If leaving root rule restore previous root rule name.
            if self.rule_name:
                parser.in_rule = previous_root_rule_name

        # For root rules flatten non-terminal/list
        if self.root and result and not isinstance(result, Terminal):
            if not isinstance(result, NonTerminal):
                result = flatten(result)

            # Tree reduction will eliminate Non-terminal with single child.
            if parser.reduce_tree and len(result) == 1:
                result = result[0]

            # If the result is not parse tree node it must be a plain list
            # so create a new NonTerminal.
            if not isinstance(result, ParseTreeNode):
                result = NonTerminal(self, result)

        # Result caching for use by memoization.
        if parser.memoization:
            self._result_cache[c_pos] = (result, parser.position)

        return result


class NoMatch(Exception):
    """
    Exception raised by the Match classes during parsing to indicate that the
    match is not successful.

    Args:
        rules (list of ParsingExpression): Rules that are tried at the position
            of the exception.
        position (int): A position in the input stream where exception
            occurred.
        parser (Parser): An instance of a parser.
    """
    def __init__(self, rules: List[ParsingExpression], position, parser) -> None:
        self.rules = rules
        self.position = position
        self.parser = parser

    def __str__(self) -> str:
        def rule_to_exp_str(rule) -> str:
            if hasattr(rule, '_exp_str'):
                # Rule may override expected report string
                return rule._exp_str
            elif rule.root:
                return rule.rule_name
            elif isinstance(rule, Match) and \
                    not isinstance(rule, EndOfFile):
                return "'{}'".format(rule.to_match)
            else:
                return rule.name

        if not self.rules:
            err_message = "Not expected input"
        else:
            what_is_expected = ["{}".format(rule_to_exp_str(r))
                                for r in self.rules]
            what_str = " or ".join(what_is_expected)
            err_message = "Expected {}".format(what_str)

        return "{} at position {}{} => '{}'."\
            .format(err_message,
                    "{}:".format(self.parser.file_name)
                    if self.parser.file_name else "",
                    str(self.parser.pos_to_linecol(self.position)),
                    self.parser.context(position=self.position))

    def __unicode__(self):
        return self.__str__()


class Sequence(ParsingExpression):
    """
    Will match sequence of parser expressions in exact order they are defined.
    """

    def __init__(self, *elements, **kwargs):
        super(Sequence, self).__init__(*elements, **kwargs)
        self.ws = kwargs.pop('ws', None)
        self.skipws = kwargs.pop('skipws', None)

    def _parse(self, parser):
        results = []
        c_pos = parser.position

        if self.ws is not None:
            old_ws = parser.ws
            parser.ws = self.ws

        if self.skipws is not None:
            old_skipws = parser.skipws
            parser.skipws = self.skipws

        # Prefetching
        append = results.append

        try:
            for e in self.nodes:
                result = e.parse(parser)
                if result:
                    append(result)

        except NoMatch:
            parser.position = c_pos     # Backtracking
            raise

        finally:
            if self.ws is not None:
                parser.ws = old_ws
            if self.skipws is not None:
                parser.skipws = old_skipws

        if results:
            return results


class OrderedChoice(Sequence):
    """
    Will match one of the parser expressions specified. Parser will try to
    match expressions in the order they are defined.
    """
    def _parse(self, parser):
        result = None
        match = False
        c_pos = parser.position

        if self.ws is not None:
            old_ws = parser.ws
            parser.ws = self.ws

        if self.skipws is not None:
            old_skipws = parser.skipws
            parser.skipws = self.skipws

        try:
            for e in self.nodes:
                try:
                    result = e.parse(parser)
                    if result is not None:
                        match = True
                        result = [result]
                        break
                except NoMatch:
                    parser.position = c_pos  # Backtracking
        finally:
            if self.ws is not None:
                parser.ws = old_ws
            if self.skipws is not None:
                parser.skipws = old_skipws

        if not match:
            parser._nm_raise(self, c_pos, parser)

        return result


class Repetition(ParsingExpression):
    """
    Base class for all repetition-like parser expressions (?,*,+)
    Args:
        eolterm(bool): Flag that indicates that end of line should
            terminate repetition match.
    """
    def __init__(self, *elements, **kwargs):
        super(Repetition, self).__init__(*elements, **kwargs)
        self.eolterm = kwargs.get('eolterm', False)
        self.sep = kwargs.get('sep', None)


class Optional(Repetition):
    """
    Optional will try to match parser expression specified and will not fail
    in case match is not successful.
    """
    def _parse(self, parser):
        result = None
        c_pos = parser.position

        try:
            result = [self.nodes[0].parse(parser)]
        except NoMatch:
            parser.position = c_pos  # Backtracking

        return result


class ZeroOrMore(Repetition):
    """
    ZeroOrMore will try to match parser expression specified zero or more
    times. It will never fail.
    """
    def _parse(self, parser):
        results = []

        if self.eolterm:
            # Remember current eolterm and set eolterm of
            # this repetition
            old_eolterm = parser.eolterm
            parser.eolterm = self.eolterm

        # Prefetching
        append = results.append
        p = self.nodes[0].parse
        sep = self.sep.parse if self.sep else None
        result = None

        while True:
            try:
                c_pos = parser.position
                if sep and result:
                    sep_result = sep(parser)
                    if not sep_result:
                        break
                    append(sep_result)
                result = p(parser)
                if not result:
                    break
                append(result)
            except NoMatch:
                parser.position = c_pos  # Backtracking
                break

        if self.eolterm:
            # Restore previous eolterm
            parser.eolterm = old_eolterm

        return results


class OneOrMore(Repetition):
    """
    OneOrMore will try to match parser expression specified one or more times.
    """
    def _parse(self, parser):
        results = []
        first = True

        if self.eolterm:
            # Remember current eolterm and set eolterm of
            # this repetition
            old_eolterm = parser.eolterm
            parser.eolterm = self.eolterm

        # Prefetching
        append = results.append
        p = self.nodes[0].parse
        sep = self.sep.parse if self.sep else None
        result = None

        try:
            while True:
                try:
                    c_pos = parser.position
                    if sep and result:
                        sep_result = sep(parser)
                        if not sep_result:
                            break
                        append(sep_result)
                    result = p(parser)
                    if not result:
                        break
                    append(result)
                    first = False
                except NoMatch:
                    parser.position = c_pos  # Backtracking

                    if first:
                        raise

                    break
        finally:
            if self.eolterm:
                # Restore previous eolterm
                parser.eolterm = old_eolterm

        return results


class UnorderedGroup(Repetition):
    """
    Will try to match all of the parsing expression in any order.
    """
    def _parse(self, parser):
        results = []
        c_pos = parser.position

        if self.eolterm:
            # Remember current eolterm and set eolterm of
            # this repetition
            old_eolterm = parser.eolterm
            parser.eolterm = self.eolterm

        # Prefetching
        append = results.append
        nodes_to_try = set(self.nodes)
        sep = self.sep.parse if self.sep else None
        result = None
        sep_result = None
        first = True

        while nodes_to_try:
            sep_exc = None

            # Separator
            c_loc_pos_sep = parser.position
            if sep and not first:
                try:
                    sep_result = sep(parser)
                except NoMatch as exc:
                    parser.position = c_loc_pos_sep     # Backtracking

                    # This still might be valid if all remaining subexpressions
                    # are optional and none of them will match
                    sep_exc = exc

            c_loc_pos = parser.position
            match = True
            all_optionals_fail = True
            for e in set(nodes_to_try):
                try:
                    result = e.parse(parser)
                    if result:
                        if sep_exc:
                            raise sep_exc
                        if sep_result:
                            append(sep_result)
                        first = False
                        match = True
                        all_optionals_fail = False
                        append(result)
                        nodes_to_try.remove(e)
                        break

                except NoMatch:
                    match = False
                    parser.position = c_loc_pos     # local backtracking

            if not match or all_optionals_fail:
                # If sep is matched backtrack it
                parser.position = c_loc_pos_sep
                break

        if self.eolterm:
            # Restore previous eolterm
            parser.eolterm = old_eolterm

        if not match:
            # Unsucessful match of the whole PE - full backtracking
            parser.position = c_pos
            parser._nm_raise(self, c_pos, parser)

        if results:
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
        c_pos = parser.position
        for e in self.nodes:
            try:
                e.parse(parser)
            except NoMatch:
                parser.position = c_pos
                raise
        parser.position = c_pos


class Not(SyntaxPredicate):
    """
    This predicate will succeed if the specified expression doesn't match
    current input.
    """
    def _parse(self, parser):
        c_pos = parser.position
        old_in_not = parser.in_not
        parser.in_not = True
        try:
            for e in self.nodes:
                try:
                    e.parse(parser)
                except NoMatch:
                    parser.position = c_pos
                    return
            parser.position = c_pos
            parser._nm_raise(self, c_pos, parser)
        finally:
            parser.in_not = old_in_not


class Empty(SyntaxPredicate):
    """
    This predicate will always succeed without consuming input.
    """
    def _parse(self, parser):
        pass


class Decorator(ParsingExpression):
    """
    Decorator are special kind of parsing expression used to mark
    a containing pexpression and give it some special semantics.
    For example, decorators are used to mark pexpression as lexical
    rules (see :class:Lex).
    """


class Combine(Decorator):
    """
    This decorator defines pexpression that represents a lexeme rule.
    This rules will always return a Terminal parse tree node.
    Whitespaces will be preserved. Comments will not be matched.
    """
    def _parse(self, parser):
        results = []

        oldin_lex_rule = parser.in_lex_rule
        parser.in_lex_rule = True
        c_pos = parser.position
        try:
            for parser_model_node in self.nodes:
                results.append(parser_model_node.parse(parser))

            results = flatten(results)

            # Create terminal from result
            return Terminal(self, c_pos,
                            "".join([x.flat_str() for x in results]))
        except NoMatch:
            parser.position = c_pos  # Backtracking
            raise
        finally:
            parser.in_lex_rule = oldin_lex_rule


class Match(ParsingExpression):
    """
    Base class for all classes that will try to match something from the input.
    """
    def __init__(self, rule_name, root=False):
        self.to_match = None
        super().__init__(rule_name=rule_name, root=root)

    @property
    def name(self):
        if self.root:
            return "%s=%s(%s)" % (self.rule_name, self.__class__.__name__, self.to_match)
        else:
            return "%s(%s)" % (self.__class__.__name__, self.to_match)

    def _parse_comments(self, parser):
        """Parse comments."""

        try:
            parser.in_parse_comments = True
            if parser.comments_model:
                try:
                    while True:
                        # TODO: Consumed whitespaces and comments should be
                        #       attached to the first match ahead.
                        parser.comments.append(
                            parser.comments_model.parse(parser))
                        if parser.skipws:
                            # Whitespace skipping
                            pos = parser.position
                            ws = parser.ws
                            i = parser.input
                            length = len(i)
                            while pos < length and i[pos] in ws:
                                pos += 1
                            parser.position = pos
                except NoMatch:
                    # NoMatch in comment matching is perfectly
                    # legal and no action should be taken.
                    pass
        finally:
            parser.in_parse_comments = False

    def parse(self, parser):

        if parser.skipws and not parser.in_lex_rule:
            # Whitespace skipping
            pos = parser.position
            ws = parser.ws
            i = parser.input
            length = len(i)
            while pos < length and i[pos] in ws:
                pos += 1
            parser.position = pos

        if parser.debug:
            parser.dprint(
                "?? Try match rule {}{} at position {} => {}"
                .format(self.name,
                        " in {}".format(parser.in_rule)
                        if parser.in_rule else "",
                        parser.position,
                        parser.context()))

        if parser.skipws and parser.position in parser.comment_positions:
            # Skip comments if already parsed.
            parser.position = parser.comment_positions[parser.position]
        else:
            if not parser.in_parse_comments and not parser.in_lex_rule:
                comment_start = parser.position
                self._parse_comments(parser)
                parser.comment_positions[comment_start] = parser.position

        result = self._parse(parser)
        if not self.suppress:
            return result


class RegExMatch(Match):
    '''
    This Match class will perform input matching based on Regular Expressions.

    Args:
        to_match (regex string): A regular expression string to match.
            It will be used to create regular expression using re.compile.
        ignore_case(bool): If case insensitive match is needed.
            Default is None to support propagation from global parser setting.
        multiline(bool): allow regex to works on multiple lines
            (re.DOTALL flag). Default is None to support propagation from
            global parser setting.
        str_repr(str): A string that is used to represent this regex.
        re_flags: flags parameter for re.compile if neither ignore_case
            or multiple are set.

    '''
    def __init__(self, to_match, rule_name='', root=False, ignore_case=None,
                 multiline=None, str_repr=None, re_flags=re.MULTILINE):
        super(RegExMatch, self).__init__(rule_name, root)
        self.to_match_regex = to_match
        self.ignore_case = ignore_case
        self.multiline = multiline
        self.explicit_flags = re_flags
        self.to_match = str_repr if str_repr is not None else to_match

    def compile(self):
        flags = self.explicit_flags
        if self.multiline is True:
            flags |= re.DOTALL
        if self.multiline is False and flags & re.DOTALL:
            flags -= re.DOTALL
        if self.ignore_case is True:
            flags |= re.IGNORECASE
        if self.ignore_case is False and flags & re.IGNORECASE:
            flags -= re.IGNORECASE
        self.regex = re.compile(self.to_match_regex, flags)

    def __str__(self):
        return self.to_match

    def __unicode__(self):
        return self.__str__()

    def _parse(self, parser):
        c_pos = parser.position
        m = self.regex.match(parser.input, c_pos)
        if m:
            matched = m.group()
            if parser.debug:
                parser.dprint(
                    "++ Match '%s' at %d => '%s'" %
                    (matched, c_pos, parser.context(len(matched))))
            parser.position += len(matched)
            if matched:
                return Terminal(self, c_pos, matched, extra_info=m)
        else:
            if parser.debug:
                parser.dprint("-- NoMatch at {}".format(c_pos))
            parser._nm_raise(self, c_pos, parser)


class StrMatch(Match):
    """
    This Match class will perform input matching by a string comparison.

    Args:
        to_match (str): A string to match.
        ignore_case(bool): If case insensitive match is needed.
            Default is None to support propagation from global parser setting.
    """
    def __init__(self, to_match, rule_name='', root=False, ignore_case=None):
        super(StrMatch, self).__init__(rule_name, root)
        self.to_match = to_match
        self.ignore_case = ignore_case

    def _parse(self, parser):
        c_pos = parser.position
        input_frag = parser.input[c_pos:c_pos + len(self.to_match)]
        if self.ignore_case:
            match = input_frag.lower() == self.to_match.lower()
        else:
            match = input_frag == self.to_match
        if match:
            if parser.debug:
                parser.dprint(
                    "++ Match '{}' at {} => '{}'"
                    .format(self.to_match, c_pos,
                            parser.context(len(self.to_match))))
            parser.position += len(self.to_match)

            # If this match is inside sequence than mark for suppression
            suppress = type(parser.last_pexpression) is Sequence

            return Terminal(self, c_pos, self.to_match, suppress=suppress)
        else:
            if parser.debug:
                parser.dprint(
                    "-- No match '{}' at {} => '{}'"
                    .format(self.to_match, c_pos,
                            parser.context(len(self.to_match))))
            parser._nm_raise(self, c_pos, parser)

    def __str__(self):
        return self.to_match

    def __unicode__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.to_match == str(other)

    def __hash__(self):
        return hash(self.to_match)


# HACK: Kwd class is a bit hackish. Need to find a better way to
#       introduce different classes of string tokens.
class Kwd(StrMatch):
    """
    A specialization of StrMatch to specify keywords of the language.
    """
    def __init__(self, to_match):
        super(Kwd, self).__init__(to_match)
        self.to_match = to_match
        self.root = True
        self.rule_name = 'keyword'


class EndOfFile(Match):
    """
    The Match class that will succeed in case end of input is reached.
    """
    def __init__(self):
        super(EndOfFile, self).__init__("EOF")

    @property
    def name(self):
        return "EOF"

    def _parse(self, parser):
        c_pos = parser.position
        if len(parser.input) == c_pos:
            return Terminal(EOF(), c_pos, '', suppress=True)
        else:
            if parser.debug:
                parser.dprint("!! EOF not matched.")
            parser._nm_raise(self, c_pos, parser)


def EOF():
    return EndOfFile()
