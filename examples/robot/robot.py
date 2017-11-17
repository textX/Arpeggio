#######################################################################
# Name: robot.py
# Purpose: Simple DSL for defining robot movement.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2011-2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This example is inspired by an example from LISA tool (http://labraj.uni-mb.si/lisa/)
# presented during the lecture given by prof. Marjan Mernik (http://lpm.uni-mb.si/mernik/)
# at the University of Novi Sad in June, 2011.
#
# An example of the robot program:
#    begin
#        up
#        up
#        left
#        down
#        right
#    end
#######################################################################
from __future__ import print_function, unicode_literals

import os
from arpeggio import ZeroOrMore, EOF, PTNodeVisitor, ParserPython, \
    visit_parse_tree
from arpeggio.export import PMDOTExporter, PTDOTExporter

# Grammar rules
def robot():      return 'begin', ZeroOrMore(command), 'end', EOF
def command():      return [UP, DOWN, LEFT, RIGHT]
def UP():           return 'up'
def DOWN():         return 'down'
def LEFT():         return 'left'
def RIGHT():        return 'right'


# Semantic actions visitor
class RobotVisitor(PTNodeVisitor):

    def visit_robot(self, node, children):
        if self.debug:
            print("Evaluating position")
        position = [0, 0]
        for move in children:
            position[0] += move[0]
            position[1] += move[1]
        return position

    def visit_command(self, node, children):
        if self.debug:
            print("Command")
        return children[0]

    def visit_UP(self, node, children):
        if self.debug:
            print("Going up")
        return (0, 1)

    def visit_DOWN(self, node, children):
        if self.debug:
            print("Going down")
        return (0, -1)

    def visit_LEFT(self, node, children):
        if self.debug:
            print("Going left")
        return (-1, 0)

    def visit_RIGHT(self, node, children):
        if self.debug:
            print("Going right")
        return (1, 0)


def main(debug=False):

    # Load program
    current_dir = os.path.dirname(__file__)
    input_program = open(os.path.join(current_dir, 'program.rbt'), 'r').read()

    # First we will make a parser - an instance of the robot parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = ParserPython(robot, debug=debug)

    # We create a parse tree out of textual input
    parse_tree = parser.parse(input_program)

    # visit_parse_tree will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be the final position of the robot.
    result = visit_parse_tree(parse_tree, RobotVisitor(debug=debug))

    if debug:
        print("position = ", result)


if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)
