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
from __future__ import print_function

from arpeggio import *

# Grammar rules
def robot():      return Kwd('begin'), ZeroOrMore(command), Kwd('end'), EOF
def command():      return [up, down, left, right]
def up():           return 'up'
def down():         return 'down'
def left():         return 'left'
def right():        return 'right'


# Semantic actions
class Up(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Going up")
        return (0, 1)


class Down(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Going down")
        return (0, -1)


class Left(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Going left")
        return (-1, 0)


class Right(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Going right")
        return (1, 0)


class Command(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Command")
        return children[0]


class Robot(SemanticAction):
    def first_pass(self, parser, node, children):
        if parser.debug:
            print("Evaluating position")
        position = [0, 0]
        for move in children:
            position[0] += move[0]
            position[1] += move[1]
        return position

# Connecting rules with semantic actions
robot.sem = Robot()
command.sem = Command()
up.sem = Up()
down.sem = Down()
left.sem = Left()
right.sem = Right()

def main(debug=False):
    # Program code
    input_program = '''
        begin
            up
            up
            left
            down
            right
        end
    '''

    # First we will make a parser - an instance of the robot parser model.
    # Parser model is given in the form of python constructs therefore we
    # are using ParserPython class.
    parser = ParserPython(robot, debug=debug)

    # We create a parse tree out of textual input
    parse_tree = parser.parse(input_program)

    # getASG will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be the final position of the robot.
    result = parser.getASG()

    if debug:
        print("position = ", result)

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    main(debug=True)

