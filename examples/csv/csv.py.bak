##############################################################################
# Name: csv.py
# Purpose: Implementation of CSV parser in arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
##############################################################################

from __future__ import unicode_literals
import pprint
import os
from arpeggio import *
from arpeggio import RegExMatch as _

def record():                   return field, ZeroOrMore(",", field)
def field():                    return [quoted_field, field_content]
def quoted_field():             return '"', field_content_quoted, '"'
def field_content():            return _(r'([^,\n])+')
def field_content_quoted():     return _(r'(("")|([^"]))+')
def csvfile():                  return OneOrMore([record, '\n']), EOF


class CSVVisitor(PTNodeVisitor):
    def visit_field(self, node, children):
        value = children[0]
        try:
            return float(value)
        except:
            pass
        try:
            return int(value)
        except:
            return value

    def visit_record(self, node, children):
        # record is a list of fields. The children nodes are fields so just
        # transform it to list.
        return list(children)

    def visit_csvfile(self, node, children):
        # We are not interested in newlines so we will filter them.
        return [x for x in children if x!='\n']



def main(debug=False):
    # First we will make a parser - an instance of the CVS parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    # Skipping of whitespace will be done only for tabs and spaces. Newlines
    # have semantics in csv files. They are used to separate records.
    parser = ParserPython(csvfile, ws='\t ', debug=debug)

    # Creating parse tree out of textual input
    current_dir = os.path.dirname(__file__)
    test_data = open(os.path.join(current_dir, 'test_data.csv'), 'r').read()
    parse_tree = parser.parse(test_data)

    # Create list of lists using visitor
    csv_content = visit_parse_tree(parse_tree, CSVVisitor())
    print("This is a list of lists with the data from CSV file.")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(csv_content)

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

