#-*- coding: utf-8 -*-
#######################################################################
# Name: bibtex.py
# Purpose: Parser for bibtex files
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2013-2015 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import print_function, unicode_literals

import pprint
import os
import sys
from arpeggio import *
from arpeggio import RegExMatch as _


# Grammar
def bibfile():                  return ZeroOrMore([comment_entry, bibentry, comment]), EOF
def comment_entry():            return "@comment", "{", _(r'[^}]*'), "}"
def bibentry():                 return bibtype, "{", bibkey, ",", field, ZeroOrMore(",", field), "}"
def field():                    return fieldname, "=", fieldvalue
def fieldvalue():               return [fieldvalue_braces, fieldvalue_quotes]
def fieldvalue_braces():        return "{", fieldvalue_braced_content, "}"
def fieldvalue_quotes():        return '"', fieldvalue_quoted_content, '"'

# Lexical rules
def fieldname():                return _(r'[-\w]+')
def comment():                  return _(r'[^@]+')
def bibtype():                  return _(r'@\w+')
def bibkey():                   return _(r'[^\s,]+')
def fieldvalue_quoted_content():    return _(r'((\\")|[^"])*')
def fieldvalue_braced_content():    return Combine(
                                            ZeroOrMore([Optional(And("{"), fieldvalue_inner),\
                                                        fieldvalue_part]))

def fieldvalue_part():          return _(r'((\\")|[^{}])+')
def fieldvalue_inner():         return "{", fieldvalue_braced_content, "}"


# Semantic actions visitor
class BibtexVisitor(PTNodeVisitor):

    def visit_bibfile(self, node, children):
        """
        Just returns list of child nodes (bibentries).
        """
        if self.debug:
            print("Processing Bibfile")

        # Return only dict nodes
        return [x for x in children if type(x) is dict]

    def visit_bibentry(self, node, children):
        """
        Constructs a map where key is bibentry field name.
        Key is returned under 'bibkey' key. Type is returned under 'bibtype'.
        """
        if self.debug:
            print("  Processing bibentry %s" % children[1])
        bib_entry_map = {
            'bibtype': children[0],
            'bibkey': children[1]
        }
        for field in children[2:]:
            bib_entry_map[field[0]] = field[1]
        return bib_entry_map

    def visit_field(self, node, children):
        """
        Constructs a tuple (fieldname, fieldvalue).
        """
        if self.debug:
            print("    Processing field %s" % children[0])
        field = (children[0], children[1])
        return field

    def visit_fieldvalue(self, node, children):
        """
        This example is used in practice at the University of Novi Sad.
        Thus, handle accented chars found in writtings in Serbian language.
        Remove braces. Remove newlines.
        """
        value = children[0]
        value = value.replace(r"\'{c}", "ć")\
                     .replace(r"\'{C}", "Ć")\
                     .replace(r"\v{c}", "č")\
                     .replace(r"\v{C}", "Č")\
                     .replace(r"\v{z}", "ž")\
                     .replace(r"\v{Z}", "Ž")\
                     .replace(r"\v{s}", "š")\
                     .replace(r"\v{S}", "Š")
        value = re.sub("[\n{}]", '', value)
        return value


def main(debug=False, file_name=None):
    # First we will make a parser - an instance of the bib parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = ParserPython(bibfile, debug=debug)

    if not file_name:
        file_name = os.path.join(os.path.dirname(__file__),
                                 'bibtex_example.bib')

    with codecs.open(file_name, "r", encoding="utf-8") as bibtexfile:
        bibtexfile_content = bibtexfile.read()

    # We create a parse tree or abstract syntax tree out of
    # textual input
    parse_tree = parser.parse(bibtexfile_content)

    # visit_parse_tree will start semantic analysis.
    # In this case semantic analysis will return list of bibentry maps.
    ast = visit_parse_tree(parse_tree, BibtexVisitor(debug=debug))

    return ast

if __name__ == "__main__":
    # First parameter is bibtex file
    if len(sys.argv) > 1:
        # In debug mode dot (graphviz) files for parser model
        # and parse tree will be created for visualization.
        # Checkout current folder for .dot files.
        entries = main(debug=True, file_name=sys.argv[1])
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(entries)
    else:
        print("Usage: python bibtex.py file_to_parse")
