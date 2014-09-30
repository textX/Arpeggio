##############################################################################
# Name: csv.py
# Purpose: Implementation of CSV parser in arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
##############################################################################

from __future__ import unicode_literals
from arpeggio import *
from arpeggio import RegExMatch as _

def record():                   return field, ZeroOrMore(",", field)
def field():                    return [quoted_field, field_content]
def quoted_field():             return '"', field_content_quoted, '"'
def field_content():            return _(r'([^,\n])+')
def field_content_quoted():     return _(r'(("")|([^"]))+')
def csvfile():                  return OneOrMore([record, '\n']), EOF

test_data = '''
Unquoted test, "Quoted test", 23234, One Two Three, "343456.45"

Unquoted test 2, "Quoted test with ""inner"" quotes", 23234, One Two Three, "343456.45"
Unquoted test 3, "Quoted test 3", 23234, One Two Three, "343456.45"
'''

def main(debug=False):
    # First we will make a parser - an instance of the CVS parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    # Skipping of whitespace will be done only for tabs and spaces. Newlines
    # have semantics in csv files. They are used to separate records.
    parser = ParserPython(csvfile, ws='\t ', reduce_tree=True, debug=debug)

    # Creating parse tree out of textual input
    parse_tree = parser.parse(test_data)

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

