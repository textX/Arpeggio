##############################################################################
# Name: csv.py
# Purpose: Implementation of CSV parser in arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
##############################################################################
from arpeggio import *
from arpeggio.export import PMDOTExporter, PTDOTExporter
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

    if debug:
        # Then we export it to a dot file in order to visualise it.
        # This step is optional but it is handy for debugging purposes.
        # We can make a png out of it using dot (part of graphviz) like this:
        # dot -O -Tpng calc_parse_tree_model.dot
        PMDOTExporter().exportFile(parser.parser_model, "csv_parse_tree_model.dot")

    # Creating parse tree out of textual input
    parse_tree = parser.parse(test_data)

    if debug:
        # Then we export it to a dot file in order to visualise it.
        # This is also optional.
        # dot -O -Tpng calc_parse_tree.dot
        PTDOTExporter().exportFile(parse_tree, "csv_parse_tree.dot")

if __name__ == "__main__":
    main(debug=True)

