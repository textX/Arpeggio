
# proj
try:
    # imports for local pytest
    from .arpeggio import *                 # type: ignore # pragma: no cover
except ImportError:                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import *                 # type: ignore # pragma: no cover


class GrammarBase(object):
    """
    Base Class for Grammar Rules ParserPythonClass
    """


class ParserPythonClass(Parser):

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
            from .export import PMDOTExporter
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
        __for_resolving = []  # Expressions that needs cross reference resolving
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
        assert self.__cross_refs == 0, "Not all cross references are resolved!"
        return parser_model

    def errors(self):
        pass
