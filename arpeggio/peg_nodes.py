# ---------------------------------------------------
# Parse Tree node classes


class SemanticActionResults(list):
    """
    Used in visitor methods call to supply results of semantic analysis
    of children parse tree nodes.
    Enables dot access by the name of the rule similar to NonTerminal
    tree navigation.
    Enables index access as well as iteration.
    """
    def __init__(self):
        self.results = {}

    def append_result(self, name, result):
        if name:
            if name not in self.results:
                self.results[name] = []
            self.results[name].append(result)

        self.append(result)

    def __getattr__(self, attr_name):
        if attr_name == 'results':
            raise AttributeError

        return self.results.get(attr_name, [])



class ParseTreeNode(object):
    """
    Abstract base class representing node of the Parse Tree.
    The node can be terminal(the leaf of the parse tree) or non-terminal.

    Attributes:
        rule (ParsingExpression): The rule that created this node.
        rule_name (str): The name of the rule that created this node if
            root rule or empty string otherwise.
        position (int): A position in the input stream where the match
            occurred.
        position_end (int, read-only): A position in the input stream where
            the node ends.
            This position is one char behind the last char contained in this
            node. Thus, position_end - position = length of the node.
        error (bool): Is this a false parse tree node created during error
            recovery.
        comments : A parse tree of comment(s) attached to this node.
    """
    def __init__(self, rule, position, error):
        assert rule
        assert rule.rule_name is not None
        self.rule = rule
        self.rule_name = rule.rule_name
        self.position = position
        self.error = error
        self.comments = None

    @property
    def name(self):
        return "%s [%s]" % (self.rule_name, self.position)

    @property
    def position_end(self):
        "Must be implemented in subclasses."
        raise NotImplementedError

    def visit(self, visitor):
        """
        Visitor pattern implementation.

        Args:
            visitor(PTNodeVisitor): The visitor object.
        """
        if visitor.debug:
            visitor.dprint("Visiting {}  type:{} str:{}"
                           .format(self.name, type(self).__name__, str(self)))

        children = SemanticActionResults()
        if isinstance(self, NonTerminal):
            for node in self:
                child = node.visit(visitor)
                # If visit returns None suppress that child node
                if child is not None:
                    children.append_result(node.rule_name, child)

        visit_name = "visit_%s" % self.rule_name
        if hasattr(visitor, visit_name):
            # Call visit method.
            result = getattr(visitor, visit_name)(self, children)

            # If there is a method with 'second' prefix save
            # the result of visit for post-processing
            if hasattr(visitor, "second_%s" % self.rule_name):
                visitor.for_second_pass.append((self.rule_name, result))

            return result

        elif visitor.defaults:
            # If default actions are enabled
            return visitor.visit__default__(self, children)


class Terminal(ParseTreeNode):
    """
    Leaf node of the Parse Tree. Represents matched string.

    Attributes:
        rule (ParsingExpression): The rule that created this terminal.
        position (int): A position in the input stream where match occurred.
        value (str): Matched string at the given position or missing token
            name in the case of an error node.
        suppress(bool): If True this terminal can be ignored in semantic
            analysis.
        extra_info(object): additional information (e.g. the re matcher
            object)
    """

    __slots__ = ['rule', 'rule_name', 'position', 'error', 'comments',
                 'value', 'suppress', 'extra_info']

    def __init__(self, rule, position, value, error=False, suppress=False,
                 extra_info=None):
        super(Terminal, self).__init__(rule, position, error)
        self.value = value
        self.suppress = suppress
        self.extra_info = extra_info

    @property
    def desc(self):
        if self.value:
            return "%s '%s' [%s]" % (self.rule_name, self.value, self.position)
        else:
            return "%s [%s]" % (self.rule_name, self.position)

    @property
    def position_end(self):
        return self.position + len(self.value)

    def flat_str(self):
        return self.value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.desc

    def __eq__(self, other):
        return str(self) == str(other)


class NonTerminal(ParseTreeNode, list):
    """
    Non-leaf node of the Parse Tree. Represents language syntax construction.
    At the same time used in ParseTreeNode navigation expressions.
    See test_ptnode_navigation_expressions.py for examples of navigation
    expressions.

    Attributes:
        nodes (list of ParseTreeNode): Children parse tree nodes.
        _filtered (bool): Is this NT a dynamically created filtered NT.
            This is used internally.

    """

    __slots__ = ['rule', 'rule_name', 'position', 'error', 'comments',
                 '_filtered', '_expr_cache']

    def __init__(self, rule, nodes, error=False, _filtered=False):

        # Inherit position from the first child node
        position = nodes[0].position if nodes else 0

        super(NonTerminal, self).__init__(rule, position, error)

        self.extend(flatten([nodes]))
        self._filtered = _filtered

    @property
    def value(self):
        """Terminal protocol."""
        return str(self)

    @property
    def desc(self):
        return self.name

    @property
    def position_end(self):
        return self[-1].position_end if self else self.position

    def flat_str(self):
        """
        Return flatten string representation.
        """
        return "".join([x.flat_str() for x in self])

    def __str__(self):
        return " | ".join([str(x) for x in self])

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return "[ %s ]" % ", ".join([repr(x) for x in self])

    def __getattr__(self, rule_name):
        """
        Find a child (non)terminal by the rule name.

        Args:
            rule_name(str): The name of the rule that is referenced from
                this node rule.
        """
        # Prevent infinite recursion
        if rule_name in ['_expr_cache', '_filtered', 'rule', 'rule_name',
                         'position', 'append', 'extend']:
            raise AttributeError

        try:
            # First check the cache
            if rule_name in self._expr_cache:
                return self._expr_cache[rule_name]
        except AttributeError:
            # Navigation expression cache. Used for lookup by rule name.
            self._expr_cache = {}

        # If result is not found in the cache collect all nodes
        # with the given rule name and create new NonTerminal
        # and cache it for later access.
        nodes = []
        rule = None
        for n in self:
            if self._filtered:
                # For filtered NT rule_name is a rule on
                # each of its children
                for m in n:
                    if m.rule_name == rule_name:
                        nodes.append(m)
                        rule = m.rule
            else:
                if n.rule_name == rule_name:
                    nodes.append(n)
                    rule = n.rule

        result = NonTerminal(rule=rule, nodes=nodes, _filtered=True)
        self._expr_cache[rule_name] = result
        return result


def flatten(_iterable):
    """ Flattening of python iterables."""
    result = []
    for e in _iterable:
        if hasattr(e, "__iter__") and not type(e) in [str, NonTerminal]:
            result.extend(flatten(e))
        else:
            result.append(e)
    return result
