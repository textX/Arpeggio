# -*- coding: utf-8 -*-
#######################################################################
# Name: test_decorator_combine
# Purpose: Test for Combine decorator. Combine decorator
#           results in Terminal parse tree node. Whitespaces are
#           preserved  (they are not skipped) and comments are not matched.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from unittest import TestCase
from arpeggio import ParserPython, ZeroOrMore, OneOrMore, NonTerminal, Terminal, NoMatch, Combine
from arpeggio.peg import ParserPEG


class TestDecoratorCombine(TestCase):

    def test_combine_python(self):

        # This will result in NonTerminal node
        def root():     return my_rule(), "."
        # This will result in Terminal node
        def my_rule():  return Combine(ZeroOrMore("a"), OneOrMore("b"))

        parser = ParserPython(root, debug=True)

        input1 = "abbb."

        # Whitespaces are preserved in lexical rules so the following input
        # should not be recognized.
        input2 = "a b bb."

        ptree1 = parser.parse(input1)

        def fail_nm():
            ptree2 = parser.parse(input2)

        self.assertRaises(NoMatch, fail_nm)

        self.assertIsInstance(ptree1, NonTerminal)
        self.assertIsInstance(ptree1.nodes[0], Terminal)
        self.assertEqual(ptree1.nodes[0].value, "abbb")


