#-*- coding: utf-8 -*-
#######################################################################
# Name: calc.py
# Purpose: Parser for bibtex files
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example demonstrates grammar for bibtex files.
#######################################################################

import sys
from arpeggio import *
from arpeggio.export import PMDOTExport, PTDOTExport
from arpeggio import RegExMatch as _
import logging        


def bibfile():          return ZeroOrMore(bibentry), EndOfFile
def bibentry():         return bibtype, "{", bibkey, ",", field, ZeroOrMore(",", field), "}"
def bibtype():          return _(r'@\w+')
def bibkey():           return _(r'[^\s,]+'),
def field():            return fieldname, "=", '"', fieldvalue, '"'
def fieldname():        return _(r'\w+')
def fieldvalue():       return _(r'[^"]*')
def comment():          return _(r'%[^\n]*') 

# Semantic actions
class BibFileSem(SemanticAction):
    '''Just returns list of child nodes (bibentries).'''
    def first_pass(self, parser, node, nodes):
        logging.debug("Processing Bibfile")
        return nodes[:-1]        


class BibEntrySem(SemanticAction):
    '''Constructs a map where key is bibentry field name.
        Key is returned under 'bibkey' key. Type is returned under 'bibtype'.'''
    def first_pass(self, parser, node, nodes):
        logging.debug("  Processing bibentry %s" % nodes[2])
        bib_entry_map = {
            'bibtype': nodes[0].value,
            'bibkey': nodes[2].value
        }
        for field in nodes[3:]:
            if isinstance(field, tuple):
                bib_entry_map[field[0]] = field[1]
        return bib_entry_map


class FieldSem(SemanticAction):
    '''Constructs a tuple (fieldname, fieldvalue).'''
    def first_pass(self, parser, node, nodes):
        logging.debug("    Processing field %s" % nodes[0])
        field = (nodes[0].value, nodes[3])
        return field
    
    
class FieldValueSem(SemanticAction):
    '''Converts serbian letters form latex encoding to unicode.'''
    def first_pass(self, parser, node, nodes):
        return node.value.replace(r"\'{c}", u"ć")\
                    .replace(r"\'{C}", u"Ć")\
                    .replace(r"\v{c}", u"č")\
                    .replace(r"\v{C}", u"Č")\
                    .replace(r"\v{z}", u"ž")\
                    .replace(r"\v{Z}", u"Ž")\
                    .replace(r"\v{s}", u"š")\
                    .replace(r"\v{S}", u"Š")
    
# Connecting rules with semantic actions
bibfile.sem = BibFileSem()
bibentry.sem = BibEntrySem()
field.sem = FieldSem()
fieldvalue.sem = FieldValueSem()

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.DEBUG)

        # First we will make a parser - an instance of the bib parser model.
        # Parser model is given in the form of python constructs therefore we 
        # are using ParserPython class.
        parser = ParserPython(bibfile, comment_def=comment, reduce_tree=True)

        # Then we export it to a dot file in order to visualise it. This is
        # particulary handy for debugging purposes.
        # We can make a jpg out of it using dot (part of graphviz) like this
        # dot -O -Tjpg calc_parse_tree_model.dot
        PMDOTExport().exportFile(parser.parser_model,
                        "bib_parse_tree_model.dot")
                
        # First parameter is bibtex file
        if len(sys.argv) > 1:
            with open(sys.argv[1], "r") as bibtexfile:
                bibtexfile_content = bibtexfile.read()
                
                
                # We create a parse tree or abstract syntax tree out of textual input
                parse_tree = parser.parse(bibtexfile_content)
                
                # Then we export it to a dot file in order to visualise it.
                PTDOTExport().exportFile(parse_tree,
                                "bib_parse_tree.dot")

                # getASG will start semantic analysis.
                # In this case semantic analysis will list of bibentry maps.
                print parser.getASG()
        else:
            print "Usage: python bibtex.py file_to_parse"
        
    except NoMatch, e:
        print "Expected %s at position %s." % (e.value, str(e.parser.pos_to_linecol(e.position)))
