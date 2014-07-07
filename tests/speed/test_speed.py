# -*- coding: utf-8 -*-
#######################################################################
# Name: test_speed
# Purpose: Performance test of arpeggio parser
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import timeit, sys

if __name__ == "__main__":

    setup = '''
from arpeggio import OneOrMore, ZeroOrMore, EndOfFile, ParserPython, Optional
from arpeggio import RegExMatch as _

def number():           return _(r'\d*\.\d*|\d+')
def factor():           return [(Optional(["+","-"]), number), ("(", expression, ")")]
def term():             return factor, ZeroOrMore(["*","/"], factor)
def expression():       return term, ZeroOrMore(["+", "-"], term)
def calcfile():         return OneOrMore(expression), EndOfFile

parser = ParserPython(calcfile, reduce_tree=True)
with open("input.txt", "r") as f:
    input = f.read()
    '''

    print(timeit.timeit("parser.parse(input)", setup=setup, number=20))
    # 7.06 s
