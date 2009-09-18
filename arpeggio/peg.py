# -*- coding: utf-8 -*-
#######################################################################
# Name: peg.py
# Purpose: Implementing PEG language
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

__all__ = ['ParserPEG']

from arpeggio import *
from arpeggio import _log
from arpeggio import RegExMatch as _

# PEG Grammar
def grammar():          return OneOrMore(rule), EOF
def rule():             return identifier, LEFT_ARROW, ordered_choice, ";"
def ordered_choice():   return sequence, ZeroOrMore(SLASH, sequence)
def sequence():         return OneOrMore(prefix)
def prefix():           return Optional([AND,NOT]), sufix
def sufix():            return expression, Optional([QUESTION, STAR, PLUS])
def expression():       return [regex,(identifier, Not(LEFT_ARROW)), 
                                (OPEN, ordered_choice, CLOSE),
                                literal]

def regex():            return "r", "'", _(r"(\\\'|[^\'])*"),"'"
def identifier():       return _(r"[a-zA-Z_]([a-zA-Z_]|[0-9])*")
#def literal():          return [_(r"\'(\\\'|[^\'])*\'"),_(r'"[^"]*"')]
def literal():          return _(r'(\'(\\\'|[^\'])*\')|("[^"]*")')

def LEFT_ARROW():       return "<-"
def SLASH():            return "/"
def STAR():             return "*"
def QUESTION():         return "?"
def PLUS():             return "+"
def AND():              return "&"
def NOT():              return "!"
def OPEN():             return "("
def CLOSE():            return ")"

def comment():          return "//", _(".*\n")


# ------------------------------------------------------------------
# PEG Semantic Actions
class PEGSemanticAction(SemanticAction):
    def second_pass(self, parser, node):
        if isinstance(node, Terminal):
            return
        for i,n in enumerate(node.nodes):
            if isinstance(n, Terminal):
                if parser.peg_rules.has_key(n.value):
                    node.nodes[i] = parser.peg_rules[n.value]
                else:
                    raise SemanticError("Rule \"%s\" does not exists." % n)

class SemGrammar(SemanticAction):
    def first_pass(self, parser, node, nodes):
        return parser.peg_rules[parser.root_rule_name]
                    
class SemRule(PEGSemanticAction):
    def first_pass(self, parser, node, nodes):
        rule_name = nodes[0].value
        if len(nodes)>4:
            retval = Sequence(nodes=nodes[2:-1])
        else:
            retval = nodes[2]
        retval.rule = rule_name
        retval.root = True
        
        if not hasattr(parser, "peg_rules"):
            parser.peg_rules = {}   # Used for linking phase
            parser.peg_rules["EndOfFile"] = EndOfFile()        
            
        parser.peg_rules[rule_name] = retval
        return retval

class SemSequence(PEGSemanticAction):
    def first_pass(self, parser, node, nodes):
        if len(nodes)>1:
            return Sequence(nodes=nodes)
        else:
             return nodes[0]

class SemOrderedChoice(PEGSemanticAction):
    def first_pass(self, parser, node, nodes):
        if len(nodes)>1:
            retval = OrderedChoice(nodes=nodes[::2])
        else:
            retval = nodes[0]
        return retval

class SemPrefix(PEGSemanticAction):
    def first_pass(self, parser, node, nodes):
        _log("Prefix: %s " % str(nodes))
        if len(nodes)==2:
            if nodes[0] == NOT():
                retval = Not()
            else:
                retval = And()
            if type(nodes[1]) is list:
                retval.nodes = nodes[1]
            else:
                retval.nodes = [nodes[1]]
        else:
            retval = nodes[0]
            
        return retval

class SemSufix(PEGSemanticAction):
    def first_pass(self, parser, node, nodes):
        _log("Sufix : %s" % str(nodes))
        if len(nodes) == 2:
            _log("Sufix : %s" % str(nodes[1]))
            if nodes[1] == STAR():
                retval = ZeroOrMore(nodes[0])
            elif nodes[1] == QUESTION():
                retval = Optional(nodes[0])
            else:
                retval = OneOrMore(nodes[0])
            if type(nodes[0]) is list:
                retval.nodes = nodes[0]
            else:
                retval.nodes = [nodes[0]]
        else:
            retval = nodes[0]
            
        return retval

class SemExpression(PEGSemanticAction):
    def first_pass(self, parser, node, nodes):
        _log("Expression : %s" % str(nodes))
        if len(nodes)==1:
            return nodes[0]
        else:
            return nodes[1]

class SemIdentifier(SemanticAction):
    def first_pass(self, parser, node, nodes):
        _log("Identifier %s." % node.value)
        return node
    
class SemRegEx(SemanticAction):
    def first_pass(self, parser, node, nodes):
        _log("RegEx %s." % nodes[2].value)
        return RegExMatch(nodes[2].value)
    
class SemLiteral(SemanticAction):
    def first_pass(self, parser, node, nodes):
        _log("Literal: %s" % node.value)
        match_str = node.value[1:-1]
        match_str = match_str.replace("\\'", "'")
        match_str = match_str.replace("\\\\", "\\")
        return StrMatch(match_str)

class SemTerminal(SemanticAction):
    def first_pass(self, parser, node, nodes):
        return StrMatch(node.value)


grammar.sem = SemGrammar()
rule.sem = SemRule()
ordered_choice.sem = SemOrderedChoice()
sequence.sem = SemSequence()
prefix.sem = SemPrefix()
sufix.sem = SemSufix()
expression.sem = SemExpression()
regex.sem = SemRegEx()
identifier.sem = SemIdentifier()
literal.sem = SemLiteral()
for sem in [LEFT_ARROW, SLASH, STAR, QUESTION, PLUS, AND, NOT, OPEN, CLOSE]:
    sem.sem = SemTerminal()
    
    
class ParserPEG(Parser):
    def __init__(self, language_def, root_rule_name, comment_rule_name=None, skipws=True, ws=DEFAULT_WS):
        super(ParserPEG, self).__init__(skipws, ws)
        self.root_rule_name = root_rule_name
        
        # PEG Abstract Syntax Graph
        self.parser_model = self._from_peg(language_def)
                
        # Comments should be optional and there can be more of them
        if self.comments_model: # and not isinstance(self.comments_model, ZeroOrMore):
            self.comments_model.root = True
            self.comments_model.rule = comment_rule_name
            
    def _parse(self):
        return self.parser_model.parse(self)

    def _from_peg(self, language_def):
        parser = ParserPython(grammar, comment)
        parser.root_rule_name = self.root_rule_name
        parse_tree = parser.parse(language_def)
        return parser.getASG()
    
if __name__ == "__main__":
    try:
        parser = ParserPython(grammar, None)
            
        f = open("peg_parser_model.dot", "w")
        f.write(str(DOTSerializator(parser.parser_model)))
        f.close()
        
    except NoMatch, e:
        print "Expected %s at position %s." % (e.value, str(e.parser.pos_to_linecol(e.position)))
            