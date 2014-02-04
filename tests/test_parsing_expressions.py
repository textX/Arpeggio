# -*- coding: utf-8 -*-
#######################################################################
# Name: test_parsing_expressions
# Purpose: Test for parsing expressions.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from unittest import TestCase
from arpeggio import ParserPython, ZeroOrMore, OneOrMore, NoMatch, EOF, Optional, And, Not
from arpeggio import RegExMatch as _

class TestParsingExpression(TestCase):

    def test_sequence(self):

        def grammar():     return ("a", "b", "c")

        parser = ParserPython(grammar)

        parsed = str(parser.parse("a b c"))
        self.assertEqual(parsed, "[ a, b, c ]")

    def test_ordered_choice(self):

        def grammar():     return ["a", "b", "c"], EOF

        parser = ParserPython(grammar)

        parsed = str(parser.parse("b"))
        self.assertEqual(parsed, "[ b, EOF ]")

        parsed = str(parser.parse("c"))
        self.assertEqual(parsed, "[ c, EOF ]")

        self.assertRaises(NoMatch, lambda: parser.parse("ab"))
        self.assertRaises(NoMatch, lambda: parser.parse("bb"))

    def test_zero_or_more(self):

        def grammar():     return ZeroOrMore("a"), EOF

        parser = ParserPython(grammar)

        parsed = str(parser.parse("aaaaaaa"))
        self.assertEqual(parsed, "[ a, a, a, a, a, a, a, EOF ]")

        parsed = str(parser.parse(""))
        self.assertEqual(parsed, "[ EOF ]")

        self.assertRaises(NoMatch, lambda: parser.parse("bbb"))

    def test_one_or_more(self):

        def grammar():      return OneOrMore("a")

        parser = ParserPython(grammar)

        parsed = str(parser.parse("aaaaaaa"))
        self.assertEqual(parsed, "[ a, a, a, a, a, a, a ]")

        self.assertRaises(NoMatch, lambda: parser.parse(""))
        self.assertRaises(NoMatch, lambda: parser.parse("bbb"))

    def test_optional(self):

        def grammar():      return Optional("a"), "b", EOF

        parser = ParserPython(grammar)

        parsed = str(parser.parse("ab"))
        self.assertEqual(parsed, "[ a, b, EOF ]")

        parsed = str(parser.parse("b"))
        self.assertEqual(parsed, "[ b, EOF ]")

        self.assertRaises(NoMatch, lambda: parser.parse("aab"))
        self.assertRaises(NoMatch, lambda: parser.parse(""))


    # Syntax predicates

    def test_and(self):

        def grammar():      return "a", And("b"), ["c", "b"], EOF

        parser = ParserPython(grammar)

        parsed = str(parser.parse("ab"))
        self.assertEqual(parsed, "[ a, b, EOF ]")

        # 'And' will try to match 'b' and fail so 'c' will never get matched
        self.assertRaises(NoMatch, lambda: parser.parse("ac"))
        # 'And' will not consume 'b' from the input so second 'b' will never match
        self.assertRaises(NoMatch, lambda: parser.parse("abb"))

    def test_not(self):

        def grammar():      return "a", Not("b"), ["b", "c"], EOF

        parser = ParserPython(grammar)

        parsed = str(parser.parse("ac"))
        self.assertEqual(parsed, "[ a, c, EOF ]")

        # Not will will fail on 'b'
        self.assertRaises(NoMatch, lambda: parser.parse("ab"))
        # And will not consume 'c' from the input so 'b' will never match
        self.assertRaises(NoMatch, lambda: parser.parse("acb"))

