# -*- coding: utf-8 -*-
#######################################################################
# Name: test_python_parser
# Purpose: Testing the dot exporter.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import pytest
import os
from arpeggio.export import PMDOTExporter, PTDOTExporter

# Grammar
from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, ParserPython
from arpeggio import RegExMatch as _


def number():     return _(r'\d*\.\d*|\d+')
def factor():     return Optional(["+","-"]), [number,
                                               ("(", expression, ")")]
def term():       return factor, ZeroOrMore(["*","/"], factor)
def expression(): return term, ZeroOrMore(["+", "-"], term)
def calc():       return OneOrMore(expression), EOF


@pytest.fixture
def parser():
    return ParserPython(calc)


def test_export_parser_model(parser):
    """
    Testing parser model export
    """

    PMDOTExporter().exportFile(parser.parser_model,
                               "test_exporter_parser_model.dot")

    assert os.path.exists("test_exporter_parser_model.dot")


def test_export_parse_tree(parser):
    """
    Testing parse tree export.
    """

    parse_tree = parser.parse("-(4-1)*5+(2+4.67)+5.89/(.2+7)")
    PTDOTExporter().exportFile(parse_tree,
                               "test_exporter_parse_tree.dot")

    assert os.path.exists("test_exporter_parse_tree.dot")
