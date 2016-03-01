# -*- coding: utf-8 -*-
#######################################################################
# Name: test_speed
# Purpose: Basic performance test of arpeggio parser to check for
#   performance differences of various approaches.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import timeit

if __name__ == "__main__":

# Setup code works for python 3 only. Haven't figured out yet how to
# from __future__ import unicode_literals  in the setup code
    setup = r'''
import codecs
from arpeggio import OneOrMore, ZeroOrMore, EOF, ParserPython, Optional
from arpeggio import RegExMatch as _

def number():           return _(r'\d*\.\d*|\d+')
def factor():           return [(Optional([u"+",u"-"]), number), (u"(", expression, u")")]
def term():             return factor, ZeroOrMore([u"*",u"/"], factor)
def expression():       return term, ZeroOrMore([u"+", u"-"], term)
def calcfile():         return OneOrMore(expression), EOF
def comment():          return _(r'\/\*(.|\n)*?\*\/')

parser = ParserPython(calcfile, comment, reduce_tree=True)
with codecs.open("input_comments.txt", encoding="utf-8") as f:
    input = f.read()
    '''

    print(timeit.timeit("parser.parse(input)", setup=setup, number=20))
    # 4.4 s
