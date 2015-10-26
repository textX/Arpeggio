# -*- coding: utf-8 -*-
##############################################################################
# Name: peg_peg.py
# Purpose: PEG parser definition using PEG itself.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2015 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# PEG can be used to describe PEG.
# This example demonstrates building PEG parser using PEG based grammar of PEG
# grammar definition language.
##############################################################################

from __future__ import unicode_literals

import os
from arpeggio import *
from arpeggio.export import PMDOTExporter
from arpeggio.peg import PEGVisitor, ParserPEG


def main(debug=False):

    current_dir = os.path.dirname(__file__)
    peg_grammar = open(os.path.join(current_dir, 'peg.peg')).read()

    # ParserPEG will use ParserPython to parse peg_grammar definition and
    # create parser_model for parsing PEG based grammars
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    parser = ParserPEG(peg_grammar, 'peggrammar', debug=debug)

    # Now we will use created parser to parse the same peg_grammar used for
    # parser initialization. We can parse peg_grammar because it is specified
    # using PEG itself.
    print("PARSING")
    parse_tree = parser.parse(peg_grammar)

    # ASG should be the same as parser.parser_model because semantic
    # actions will create PEG parser (tree of ParsingExpressions).
    parser_model, comment_model = visit_parse_tree(
        parse_tree, PEGVisitor(root_rule_name='peggrammar',
                               comment_rule_name='comment',
                               ignore_case=False,
                               debug=debug))

    if debug:
        # This graph should be the same as peg_peg_parser_model.dot because
        # they define the same parser.
        PMDOTExporter().exportFile(parser_model,
                                   "peg_peg_new_parser_model.dot")

    # If we replace parser_mode with ASG constructed parser it will still
    # parse PEG grammars
    parser.parser_model = parser_model
    parser.parse(peg_grammar)

if __name__ == '__main__':
    main(debug=True)

