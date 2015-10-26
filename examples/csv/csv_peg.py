##############################################################################
# Name: csv.py
# Purpose: Implementation of CSV parser in arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014-2015 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
##############################################################################

from arpeggio import visit_parse_tree
from arpeggio.cleanpeg import ParserPEG
from csv import CSVVisitor

def main(debug=False):
    # First we will make a parser - an instance of the CVS parser model.
    # Parser model is given in the form of clean PEG description therefore we
    # are using ParserPEG class from arpeggio.clenapeg.  Grammar is loaded from
    # csv.peg file Skipping of whitespace will be done only for tabs and
    # spaces. Newlines have semantics in csv files. They are used to separate
    # records.
    csv_grammar = open('csv.peg', 'r').read()
    parser = ParserPEG(csv_grammar, 'csvfile', ws='\t ', debug=debug)

    # Creating parse tree out of textual input
    test_data = open('test_data.csv', 'r').read()
    parse_tree = parser.parse(test_data)

    # Create list of lists using visitor
    csv_content = visit_parse_tree(parse_tree, CSVVisitor())
    print(csv_content)

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

