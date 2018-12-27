##############################################################################
# Name: json.py
# Purpose: Implementation of a simple JSON parser in arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example is based on jsonParser.py from the pyparsing project
# (see http://pyparsing.wikispaces.com/).
##############################################################################

from __future__ import unicode_literals

import os
from arpeggio import *
from arpeggio import RegExMatch as _

def TRUE():     return "true"
def FALSE():    return "false"
def NULL():     return "null"
def jsonString():       return '"', _('[^"]*'),'"'
def jsonNumber():       return _('-?\d+((\.\d*)?((e|E)(\+|-)?\d+)?)?')
def jsonValue():        return [jsonString, jsonNumber, jsonObject, jsonArray, TRUE, FALSE, NULL]
def jsonArray():        return "[", Optional(jsonElements), "]"
def jsonElements():     return jsonValue, ZeroOrMore(",", jsonValue)
def memberDef():        return jsonString, ":", jsonValue
def jsonMembers():      return memberDef, ZeroOrMore(",", memberDef)
def jsonObject():       return "{", Optional(jsonMembers), "}"
def jsonFile():         return jsonObject, EOF


def main(debug=False):
    # Creating parser from parser model.
    parser = ParserPython(jsonFile, debug=debug)

    # Load test JSON file
    current_dir = os.path.dirname(__file__)
    testdata = open(os.path.join(current_dir, 'test.json')).read()

    # Parse json string
    parse_tree = parser.parse(testdata)

    # parse_tree can now be analysed and transformed to some other form
    # using e.g. visitor support. See http://textx.github.io/Arpeggio/semantics/

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

