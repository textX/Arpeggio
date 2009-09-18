# -*- coding: utf-8 -*-
##############################################################################
# Name: peg_peg.py
# Purpose: PEG parser definition using PEG itself.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
# 
# PEG can be used to describe PEG.
# This example demonstrates building PEG parser using PEG based grammar of PEG 
# grammar definition language.
##############################################################################
from arpeggio import *
from arpeggio.export import PMDOTExport, PTDOTExport
from arpeggio import _log
from arpeggio import RegExMatch as _
from arpeggio.peg import ParserPEG

# Semantic actions
from arpeggio.peg import SemGrammar, SemRule, SemOrderedChoice, SemSequence, SemPrefix, \
                SemSufix, SemExpression, SemRegEx, SemIdentifier, SemLiteral, SemTerminal

sem_actions = {
    "grammar"           : SemGrammar(),
    "rule"              : SemRule(),
    "ordered_choice"    : SemOrderedChoice(),
    "sequence"          : SemSequence(),
    "prefix"            : SemPrefix(),
    "sufix"             : SemSufix(),
    "expression"        : SemExpression(),
    "regex"             : SemRegEx(),
    "identifier"        : SemIdentifier(),
    "literal"           : SemLiteral() 
}

for sem in ["LEFT_ARROW", "SLASH", "STAR", "QUESTION", "PLUS", "AND", "NOT", "OPEN", "CLOSE"]:
    sem_actions[sem] = SemTerminal()


# PEG defined using PEG itself.
peg_grammar = r"""
 grammar <- rule+ EndOfFile;
 rule <- identifier LEFT_ARROW ordered_choice ';';
 ordered_choice <- sequence (SLASH sequence)*;
 sequence <- prefix+;
 prefix <- (AND/NOT)? sufix;
 sufix <- expression (QUESTION/STAR/PLUS)?;
 expression <- regex / (identifier !LEFT_ARROW) 
                / ("(" ordered_choice ")") / literal;

 identifier <- r'[a-zA-Z_]([a-zA-Z_]|[0-9])*';
 regex <- 'r' '\'' r'(\\\'|[^\'])*' '\'';
 literal <- r'\'(\\\'|[^\'])*\'|"[^"]*"';
 LEFT_ARROW <- '<-';
 SLASH <- '/';
 AND <- '&';
 NOT <- '!';
 QUESTION <- '?';
 STAR <- '*';
 PLUS <- '+';
 OPEN <- '(';
 CLOSE <- ')';
 DOT <- '.';
 comment <- '//' r'.*\n';
"""
    

try:
    import arpeggio
    arpeggio.DEBUG = True

    # ParserPEG will use ParserPython to parse peg_grammar definition and 
    # create parser_model for parsing PEG based grammars
    parser = ParserPEG(peg_grammar, 'grammar')
        
    # Exporting parser model to dot file in order to visualise.
    PMDOTExport().exportFile(parser.parser_model,
            "peg_peg_parser_model.dot")
    
    # Now we will use created parser to parse the same peg_grammar used for parser
    # initialization. We can parse peg_grammar because it is specified using
    # PEG itself.
    parser.parse(peg_grammar)

    PTDOTExport().exportFile(parser.parse_tree,
            "peg_peg_parse_tree.dot")
    
    # ASG should be the same as parser.parser_model because semantic
    # actions will create PEG parser (tree of ParsingExpressions).
    asg = parser.getASG(sem_actions)

    # This graph should be the same as peg_peg_parser_model.dot because
    # they define the same parser.
    PMDOTExport().exportFile(asg,
            "peg_peg_asg.dot")
    
    # If we replace parser_mode with ASG constructed parser it will still
    # parse PEG grammars
    parser.parser_model = asg
    parser.parse(peg_grammar)


except NoMatch, e:
    print "Expected %s at position %s." % (e.value, str(e.parser.pos_to_linecol(e.position)))
