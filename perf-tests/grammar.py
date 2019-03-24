#-*- coding: utf-8 -*-
#######################################################################
# Name: grammar.py
# Purpose: Grammar for Rational Rhapsody. For testing purposes.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import print_function, unicode_literals

from arpeggio import *
from arpeggio import RegExMatch as _


# Grammar
def rhapsody():                 return header, obj
def header():                   return _(r'[^\n]*')
def obj():                      return '{', ident, OneOrMore(prop), '}'
def prop():                     return '-', ident, '=', \
                                       Optional(value, \
                                                ZeroOrMore(Optional(';'), Not(['-', '}']), value)), \
                                       Optional(';')
def value():                    return [_string, _int, _float, GUID, obj, ident]
def GUID():                     return 'GUID', _(r'[a-f0-9]*-[a-f0-9]*-[a-f0-9]*-[a-f0-9]*-[a-f0-9]*')

def ident():                    return _(r'[^\d\W]\w*\b')
def _string():                  return _(r'("(\\"|[^"])*")|(\'(\\\'|[^\'])*\')')
def _int():                     return _(r'[-+]?[0-9]+\b')
def _float():                   return _(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b')
