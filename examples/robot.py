#######################################################################
# Name: robot.py
# Purpose: Simple DSL for defining robot movement.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2011 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
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
from arpeggio.export import PMDOTExporter, PTDOTExporter

# Grammar rules
def program():      return Kwd('begin'), ZeroOrMore(command), Kwd('end'), EndOfFile
def command():      return [up, down, left, right]
def up():           return 'up'
def down():         return 'down'
def left():         return 'left'
def right():        return 'right'


# Semantic actions
class Up(SemanticAction):
    def first_pass(self, parser, node, children):
        print("Going up")
        return (0, 1)

class Down(SemanticAction):
    def first_pass(self, parser, node, children):
        print("Going down")
        return (0, -1)

class Left(SemanticAction):
    def first_pass(self, parser, node, children):
        print("Going left")
        return (-1, 0)

class Right(SemanticAction):
    def first_pass(self, parser, node, children):
        print("Going right")
        return (1, 0)

class Command(SemanticAction):
    def first_pass(self, parser, node, children):
        print("Command")
        return children[0]


class Program(SemanticAction):
    def first_pass(self, parser, node, children):
        print("Evaluating position")
        position = [0, 0]
        for move in children[1:-2]:
            position[0] += move[0]
            position[1] += move[1]
        return position

# Connecting rules with semantic actions
program.sem = Program()
command.sem = Command()
up.sem = Up()
down.sem = Down()
left.sem = Left()
right.sem = Right()

if __name__ == "__main__":

    # Program code
    input = '''
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
    parser = ParserPython(program, debug=True)

    # Then we export it to a dot file in order to visualize it.
    # This step is optional but it is handy for debugging purposes.
    # We can make a png out of it using dot (part of graphviz) like this
    # dot -O -Tpng robot_parser_model.dot
    PMDOTExporter().exportFile(parser.parser_model,
                    "robot_parser_model.dot")

    # We create a parse tree out of textual input
    parse_tree = parser.parse(input)

    # Then we export it to a dot file in order to visualize it.
    # dot -O -Tpng robot_parse_tree.dot
    PTDOTExporter().exportFile(parse_tree,
                    "robot_parse_tree.dot")

    # getASG will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be the final position of the robot.
    print("position = ", parser.getASG())

