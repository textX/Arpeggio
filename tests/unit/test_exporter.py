# -*- coding: utf-8 -*-
#######################################################################
# Name: test_python_parser
# Purpose: Test for parser constructed using Python-based grammars.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import os
from unittest import TestCase
from arpeggio.export import PMDOTExporter, PTDOTExporter

# Grammar
from arpeggio import Optional, ZeroOrMore, OneOrMore, EndOfFile, ParserPython, Sequence, NonTerminal
from arpeggio import RegExMatch as _


def number():     return _(r'\d*\.\d*|\d+')
def factor():     return Optional(["+","-"]), [number,
                                               ("(", expression, ")")]
def term():       return factor, ZeroOrMore(["*","/"], factor)
def expression(): return term, ZeroOrMore(["+", "-"], term)
def calc():       return OneOrMore(expression), EndOfFile


class TestPythonParser(TestCase):

    def setUp(self):
        """
        Create parser
        """
        self.parser = ParserPython(calc)

    def test_export_parser_model(self):
        """
        Testing parser model export
        """

        PMDOTExporter().exportFile(self.parser.parser_model,
                                "test_exporter_parser_model.dot")

        self.assertTrue(os.path.exists("test_exporter_parser_model.dot"))


    def test_export_parse_tree(self):
        """
        Testing parse tree export.
        """

        parse_tree = self.parser.parse("-(4-1)*5+(2+4.67)+5.89/(.2+7)")
        PTDOTExporter().exportFile(parse_tree,
                                   "test_exporter_parse_tree.dot")

        self.assertTrue(os.path.exists("test_exporter_parse_tree.dot"))
