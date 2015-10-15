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

json_bnf = """
object
    { members }
    {}
members
    string : value
    members , string : value
array
    [ elements ]
    []
elements
    value
    elements , value
value
    string
    number
    object
    array
    true
    false
    null
"""

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


testdata = """
{
    "glossary": {
        "title": "example glossary",
        "GlossDiv": {
            "title": "S",
            "GlossList":
                {
                "ID": "SGML",
                "SortAs": "SGML",
                "GlossTerm": "Standard Generalized Markup Language",
                "TrueValue": true,
                "FalseValue": false,
                "Gravity": -9.8,
                "LargestPrimeLessThan100": 97,
                "AvogadroNumber": 6.02E23,
                "EvenPrimesGreaterThan2": null,
                "PrimesLessThan10" : [2,3,5,7],
                "Acronym": "SGML",
                "Abbrev": "ISO 8879:1986",
                "GlossDef": "A meta-markup language, used to create markup languages such as DocBook.",
                "GlossSeeAlso": ["GML", "XML", "markup"],
                "EmptyDict":  {},
                "EmptyList" : []
                }
        }
    }
}
"""

def main(debug=False):
    # Creating parser from parser model.
    parser = ParserPython(jsonFile, debug=debug)

    # Parse json string
    parse_tree = parser.parse(testdata)

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

