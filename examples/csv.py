##############################################################################
# Name: csv.py
# Purpose: Implementation of CSV parser in arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
##############################################################################
from arpeggio import *
from arpeggio.export import PMDOTExport, PTDOTExport
from arpeggio import RegExMatch as _

def newline():                  return _(r'\n+')
def record():                   return field, ZeroOrMore(",", field)
def field():                    return [quoted_field, field_content]
def quoted_field():             return '"', field_content_quoted, '"'
def field_content():            return _(r'([^,\n])+')
def field_content_quoted():     return _(r'(("")|([^"]))+')
def csvfile():                  return OneOrMore(ZeroOrMore(newline), record, OneOrMore(newline)), EndOfFile


if __name__ == "__main__":

    test_data = '''
Unquoted test, "Quoted test", 23234, One Two Three, "343456.45"

Unquoted test 2, "Quoted test 2", 23234, One Two Three, "343456.45"
Unquoted test 3, "Quoted test 3", 23234, One Two Three, "343456.45"
    '''

    try:
        # First we will make a parser - an instance of the CVS parser model.
        # Parser model is given in the form of python constructs therefore we
        # are using ParserPython class.
        # Skipping of whitespace will be done only for tabs and spaces. Newlines
        # have semantics in csv files. They are used to separate records.
        parser = ParserPython(csvfile, ws='\t ', reduce_tree=True, debug=True)

        # Then we export it to a dot file in order to visualise it. This is
        # particularly handy for debugging purposes.
        # We can make a jpg out of it using dot (part of graphviz) like this:
        # dot -O -Tpng calc_parse_tree_model.dot
        PMDOTExport().exportFile(parser.parser_model,
                                 "csv_parse_tree_model.dot")

        # Creating parse tree out of textual input
        parse_tree = parser.parse(test_data)

        # Then we export it to a dot file in order to visualise it.
        # dot -O -Tpng calc_parse_tree.dot
        PTDOTExport().exportFile(parse_tree,
                                 "csv_parse_tree.dot")

    except NoMatch, e:
        print "Expected %s at position %s." % (e.value, str(e.parser.pos_to_linecol(e.position)))
