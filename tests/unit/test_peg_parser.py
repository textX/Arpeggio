# -*- coding: utf-8 -*-
#######################################################################
# Name: test_peg_parser
# Purpose: Test for parser constructed using PEG textual grammars.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from unittest import TestCase
from arpeggio import Sequence, NonTerminal
from arpeggio.peg import ParserPEG

grammar = '''
    number <- r'\d*\.\d*|\d+';
    factor <- ("+" / "-")?
              (number / "(" expression ")");
    term <- factor (( "*" / "/") factor)*;
    expression <- term (("+" / "-") term)*;
    calc <- expression+ EOF;
'''

class TestPEGParser(TestCase):

    def test_construct_parser(self):

        parser = ParserPEG(grammar, 'calc')

        self.assertEqual(parser.parser_model.rule ,'calc')
        self.assertTrue(isinstance(parser.parser_model, Sequence))
        self.assertEqual(parser.parser_model.nodes[0].name ,'OneOrMore')

    def test_parse_input(self):

        parser = ParserPEG(grammar, 'calc')
        input = "4+5*7/3.45*-45*(2.56+32)/-56*(2-1.34)"
        result = parser.parse(input)

        self.assertTrue(isinstance(result, NonTerminal))
        self.assertEqual(str(result), "4 | + | 5 | * | 7 | / | 3.45 | * | - | 45 | * | ( | 2.56 | + | 32 | ) | / | - | 56 | * | ( | 2 | - | 1.34 | ) | ")
        self.assertEqual(repr(result),"[ [ [ [ number '4' [0] ] ],  '+' [1], [ [ number '5' [2] ],  '*' [3], [ number '7' [4] ],  '/' [5], [ number '3.45' [6] ],  '*' [10], [  '-' [11], number '45' [12] ],  '*' [14], [  '(' [15], [ [ [ number '2.56' [16] ] ],  '+' [20], [ [ number '32' [21] ] ] ],  ')' [23] ],  '/' [24], [  '-' [25], number '56' [26] ],  '*' [28], [  '(' [29], [ [ [ number '2' [30] ] ],  '-' [31], [ [ number '1.34' [32] ] ] ],  ')' [36] ] ] ], EOF [37] ]")

    def test_reduce_tree(self):

        parser = ParserPEG(grammar, 'calc', reduce_tree=True)
        input = "4+5*7/3.45*-45*(2.56+32)/-56*(2-1.34)"
        result = parser.parse(input)

        self.assertTrue(isinstance(result, NonTerminal))

        self.assertEqual(str(result),"4 | + | 5 | * | 7 | / | 3.45 | * | - | 45 | * | ( | 2.56 | + | 32 | ) | / | - | 56 | * | ( | 2 | - | 1.34 | ) | ")
        self.assertEqual(repr(result), "[ [ number '4' [0],  '+' [1], [ number '5' [2],  '*' [3], number '7' [4],  '/' [5], number '3.45' [6],  '*' [10], [  '-' [11], number '45' [12] ],  '*' [14], [  '(' [15], [ number '2.56' [16],  '+' [20], number '32' [21] ],  ')' [23] ],  '/' [24], [  '-' [25], number '56' [26] ],  '*' [28], [  '(' [29], [ number '2' [30],  '-' [31], number '1.34' [32] ],  ')' [36] ] ] ], EOF [37] ]")
