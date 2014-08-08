#######################################################################
# Name: textx.py
# Purpose: Implementation of textX language in Arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# The idea for this language is shamelessly stolen from the Xtext language
# but there are some subtle differences in both syntax and semantics.
# To make things clear I have named this language textX ;)
#######################################################################

from collections import namedtuple

from arpeggio import StrMatch, Optional, ZeroOrMore, OneOrMore, Sequence,\
    OrderedChoice, RegExMatch, NoMatch, EOF,\
    SemanticAction,ParserPython, Combine, Parser, SemanticActionSingleChild,\
    SemanticActionBodyWithBraces, Terminal, ParsingExpression
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _


# textX grammar
def textx_model():          return ZeroOrMore(rule), EOF
def rule():                 return [metaclass, enum]
def enum():                 return enum_kwd, ident, ':', enum_literal,\
                                    ZeroOrMore("|", enum_literal), ';'
def enum_literal():         return ident, '=', str_match
def metaclass():            return metaclass_name, ":", choice, ';'
def metaclass_name():       return ident

def choice():               return sequence, ZeroOrMore("|", sequence)
def sequence():             return OneOrMore(expr)

def expr():                 return [assignment, terminal_match, rule_match,
                                    bracketed_choice],\
                                    Optional(repeat_operator)
def bracketed_choice():     return '(', choice, ')'
def repeat_operator():      return ['*', '?', '+']

# Assignment
def assignment():           return attribute, assignment_op, assignment_rhs
def attribute():            return ident
def assignment_op():        return ["=", "*=", "+=", "?="]
def assignment_rhs():       return [rule_ref, list_match, terminal_match, bracketed_choice]

# Match
def match():                return [terminal_match, list_match, rule_ref]
def terminal_match():       return [str_match, re_match]
def str_match():            return [("'", _(r"((\\')|[^'])*"),"'"),\
                                    ('"', _(r'((\\")|[^"])*'),'"')]
def re_match():             return "/", _(r"((\\/)|[^/])*"), "/"

def list_match():           return "{", rule_ref, Optional(list_separator), '}'
def list_separator():       return terminal_match

# Rule reference
def rule_ref():             return [rule_match, rule_link]
def rule_match():           return ident
def rule_link():            return '[', rule_name, ']'
#def rule_choice():          return rule_name, ZeroOrMore('|', rule_name)
def rule_name():            return ident

def ident():                return _(r'\w+')
def enum_kwd():             return 'enum'

# Comments
def comment():              return [comment_line, comment_block]
def comment_line():         return _(r'//.*$')
def comment_block():        return _(r'/\*(.|\n)*?\*/')


# Special rules - primitive types
ID      = _(r'[^\d\W]\w*\b', rule_name='ID', root=True)
BOOL    = _(r'true|false|0|1', rule_name='BOOL', root=True)
INT     = _(r'[-+]?[0-9]+', rule_name='INT', root=True)
FLOAT   = _(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'FLOAT', root=True)
STRING  = _(r'("[^"]*")|(\'[^\']*\')', 'STRING', root=True)

def convert(value, _type):
    return {
            'BOOL'  : lambda x: bool(x),
            'INT'   : lambda x: int(x),
            'FLOAT' : lambda x: float(x)
            }.get(_type, lambda x: x)(value)


class RuleMatchCrossRef(object):
    """Helper class used for cross reference resolving."""
    def __init__(self, rule_name, position):
        self.rule_name = rule_name
        self.position = position


# TextX Exceptions
class TextXError(Exception):
    pass


class TextXSemanticError(TextXError):
    pass


class TextXSyntaxError(TextXError):
    pass


# TextX semantic actions
class TextXModelSA(SemanticAction):
    def first_pass(self, parser, node, children):

        class TextXLanguageParser(Parser):
            """
            Parser created from textual textX language description.
            Semantic actions for this parser will construct object
            graph representing model on the given language.
            """
            def __init__(self, *args, **kwargs):
                super(TextXLanguageParser, self).__init__(*args, **kwargs)

                # By default first rule is starting rule
                self.parser_model = children[0]
                self.comments_model = parser._peg_rules.get('__comment', None)

                # Stack for metaclass instances
                self._inst_stack = []
                # Dict for cross-ref resolving
                self._instances = {}

                self.debug = parser.debug

            def _parse(self):
                try:
                    return self.parser_model.parse(self)
                except NoMatch as e:
                    raise TextXSyntaxError(str(e))

            def get_model(self):
                return parse_tree_to_objgraph(self, self.parse_tree)


        textx_parser = TextXLanguageParser()

        textx_parser._metaclasses = parser._metaclasses
        textx_parser._peg_rules = parser._peg_rules

        return textx_parser

    def second_pass(self, parser, textx_parser):
        """Cross reference resolving for parser model."""

        if parser.debug:
            print("RESOLVING XTEXT PARSER: second_pass")

        resolved_set = set()

        def resolve(node):
            """Recursively resolve peg rule references."""

            def _inner_resolve(rule):
                if parser.debug:
                    print("Resolving rule: {}".format(rule))

                if type(rule) == RuleMatchCrossRef:
                    rule_name = rule.rule_name
                    if rule_name in textx_parser._peg_rules:
                        rule = textx_parser._peg_rules[rule_name]
                    else:
                        raise TextXSemanticError('Unexisting rule "{}" at position {}.'\
                                .format(rule.rule_name, parser.pos_to_linecol(rule.position)))

                assert isinstance(rule, ParsingExpression), type(rule)
                # Recurse
                for idx, child in enumerate(rule.nodes):
                    if not child in resolved_set:
                        resolved_set.add(rule)
                        rule.nodes[idx] = _inner_resolve(child)

                return rule

            resolved_set.add(node)
            _inner_resolve(node)

        resolve(textx_parser.parser_model)

        return textx_parser

textx_model.sem = TextXModelSA()


def metaclass_SA(parser, node, children):
    rule_name, rule = children
    rule = Sequence(nodes=[rule], rule_name=rule_name,
            root=True)

    # Do some name mangling for comment rule
    # to prevent refererencing from other rules
    if rule_name.lower() == "comment":
        rule_name = "__comment"

    parser._peg_rules[rule_name] = rule
    return rule
metaclass.sem = metaclass_SA

def metaclass_name_SA(parser, node, children):
    class Meta(object):
        """Dynamic metaclass."""
        def __str__(self):
            s = "MetaClass: {}\n".format(self.__class__.__name__)
            for attr in self.__dict__:
                if not attr.startswith('_'):
                    value = getattr(self, attr)
                    if type(value) is not list:
                        s+="\t{} = {}\n".format(attr, str(value))
                    else:
                        s+="["+",".join([str(x) for x in value]) + "]"
            return s
    name = str(node)
    cls = Meta
    cls.__name__ = name
    cls.__attrib = {}
    # TODO: Attributes and inheritance
    parser._metaclasses[name] = cls
    parser._current_metaclass = cls

    # First rule will be the root of the meta-model
    if not parser.root_rule_name:
        parser.root_rule_name = name

    return name
metaclass_name.sem = metaclass_name_SA

def sequence_SA(parser, node, children):
    return Sequence(nodes=children[:])
sequence.sem = sequence_SA

def choice_SA(parser, node, children):
    return OrderedChoice(nodes=children[:])
choice.sem = choice_SA

def assignment_SA(parser, node, children):
    """
    Create parser rule for addition and register attribute types
    on metaclass.
    """
    attr_name = children[0]
    op = children[1]
    rhs = children[2]
    mclass = parser._current_metaclass
    if attr_name in mclass.__attrib:
        raise TextXSemanticError('Multiple assignment to the same attribute "{}" at {}'\
                .format(attr_name, parser.pos_to_linecol(node.position)))
    if op == '+=':
        assignment_rule = OneOrMore(nodes=[rhs],
                rule_name='__asgn_oneormore', root=True)
        mclass.__attrib[attr_name] = list
    elif op == '*=':
        assignment_rule = ZeroOrMore(nodes=[rhs],
                rule_name='__asgn_zeroormore', root=True)
        mclass.__attrib[attr_name] = list
    elif op == '?=':
        assignment_rule = Optional(nodes=[rhs],
                rule_name='__asgn_optional', root=True)
        mclass.__attrib[attr_name] = bool
    else:
        assignment_rule = Sequence(nodes=[rhs],
                rule_name='__asgn_plain', root=True)
        # Determine type for proper initialization
        if rhs.rule_name == 'INT':
            mclass.__attrib[attr_name] = int
        elif rhs.rule_name == 'FLOAT':
            mclass.__attrib[attr_name] = float
        elif rhs.rule_name == 'BOOL':
            mclass.__attrib[attr_name] = bool
        elif rhs.rule_name == 'STRING':
            mclass.__attrib[attr_name] = str
        else:
            mclass.__attrib[attr_name] = None

    assignment_rule._attr_name = attr_name
    return assignment_rule
assignment.sem = assignment_SA

def expr_SA(parser, node, children):
    if children[1] == '?':
        return Optional(nodes=[children[0]])
    elif children[1] == '*':
        return ZeroOrMore(nodes=[children[0]])
    elif children[1] == '+':
        return OneOrMore(nodes=[children[0]])
    else:
        TextXSemanticError('Unknown repetition operand "{}" at {}'\
                .format(children[1], str(parser.pos_to_linecol(node[1].position))))
expr.sem = expr_SA

def str_match_SA(parser, node, children):
    return StrMatch(children[0], ignore_case=parser.ignore_case)
str_match.sem = str_match_SA

def re_match_SA(parser, node, children):
    to_match = children[0]
    regex = RegExMatch(to_match, ignore_case=parser.ignore_case)
    try:
        regex.compile()
    except Exception as e:
        raise TextXSyntaxError("{} at {}".format(str(e),\
            str(parser.pos_to_linecol(node[1].position))))
    return regex
re_match.sem = re_match_SA

def rule_match_SA(parser, node, children):
    return RuleMatchCrossRef(str(node), node.position)
rule_match.sem = rule_match_SA

def rule_link_SA(parser, node, children):
    # TODO: In analisys during model parsing this will be a link to some other object
    # identified by target metaclass ID
    return ID
rule_link.sem = rule_link_SA

def list_match_SA(parser, node, children):
    if len(children)==1:
        return children[0]
    else:
        match = children[0]
        separator = children[1]
        separator.rule_name = 'sep'
        return Sequence(nodes=[children[0],
                ZeroOrMore(nodes=Sequence(nodes=[separator, match]))])
list_match.sem = list_match_SA

# Default actions
bracketed_choice.sem = SemanticActionSingleChild()


def parse_tree_to_objgraph(parser, parse_tree):
    """
    Transforms parse_tree to object graph representing model in a
    new language.
    """

    def process_node(node):
        if isinstance(node, Terminal):
            return convert(node.value, node.rule_name)

        assert node.rule.root, "{}".format(node.rule.rule_name)
        # If this node is created by some root rule
        # create metaclass instance.
        inst = None
        if not node.rule_name.startswith('__asgn'):
            # If not assignment
            # Create metaclass instance
            mclass = parser._metaclasses[node.rule_name]

            # If there is no attributes collected it is an abstract rule
            # Skip it.
            if not mclass.__attrib:
                return process_node(node[0])

            inst = mclass()
            # Initialize attributes
            for attr_name, constructor in mclass.__attrib.items():
                init_value = constructor() if constructor else None
                setattr(inst, attr_name, init_value)

            parser._inst_stack.append(inst)

            for n in node:
                process_node(n)

        else:
            # Handle assignments
            attr_name = node.rule._attr_name
            op = node.rule_name.split('_')[-1]
            i = parser._inst_stack[-1]

            print('ASSIGNMENT', op, attr_name)

            if op == 'optional':
                setattr(i, attr_name, True)

            elif op == 'plain':
                attr = getattr(i, attr_name)
                # Recurse and convert value to proper type
                value = convert(process_node(node[0]), node[0].rule_name)
                if type(attr) is list:
                    attr.append(value)
                else:
                    setattr(i, attr_name, value)

            elif op in ['oneormore', 'zeroormore']:
                for n in node:
                    # If the node is separator skip
                    if n.rule_name != 'sep':
                        # Convert node to proper type
                        # Rule links will be resolved later
                        value = convert(process_node(node[0]), node[0].rule_name)
                        getattr(i, attr_name).append(value)
            else:
                # This shouldn't happen
                assert False


        # Special case for 'name' attrib. It is used for cross-referencing
        if hasattr(inst, 'name') and inst.name:
            inst.__name__ = inst.name
            parser._instances[inst.name] = inst

        if inst:
            parser._inst_stack.pop()

        return inst

    model = process_node(parse_tree)
    assert not parser._inst_stack

    return model

def get_parser(language_def, ignore_case=True, debug=False):
    # First create parser for TextX descriptions
    parser = ParserPython(textx_model, comment_def=comment,
            ignore_case=ignore_case, reduce_tree=True, debug=debug)

    # This is used during parser construction phase.
    parser._metaclasses = {}
    parser._peg_rules = {
            'ID': ID,
            'INT': INT,
            'FLOAT': FLOAT,
            'STRING': STRING,
            'BOOL': BOOL,
            }
    for regex in parser._peg_rules.values():
        regex.compile()
    parser._current_metaclass = None
    parser.root_rule_name = None

    # Parse language description with TextX parser
    try:
        parse_tree = parser.parse(language_def)
    except NoMatch as e:
        raise TextXSyntaxError(str(e))

    # Construct new parser based on the given language description.
    lang_parser = parser.getASG()

    if debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(lang_parser.parser_model,\
                "{}_parser_model.dot".format(parser.root_rule_name))

    return lang_parser




