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

from arpeggio import *
from arpeggio.export import PMDOTExport, PTDOTExport
from arpeggio import RegExMatch as _

# Grammar rules
def program():      return Kwd('begin'), ZeroOrMore(command), Kwd('end'), EndOfFile
def command():      return [up, down, left, right]
def up():           return 'up'
def down():         return 'down'
def left():         return 'left'
def right():        return 'right'


# Semantic actions
class Up(SemanticAction):
    def first_pass(self, parser, node, nodes):
        print "Going up"
        return (0, 1)

class Down(SemanticAction):
    def first_pass(self, parser, node, nodes):
        print "Going down"
        return (0, -1)

class Left(SemanticAction):
    def first_pass(self, parser, node, nodes):
        print "Going left"
        return (-1, 0)

class Right(SemanticAction):
    def first_pass(self, parser, node, nodes):
        print "Going right"
        return (1, 0)

class Command(SemanticAction):
    def first_pass(self, parser, node, nodes):
        print "Command"
        return nodes[0]


class Program(SemanticAction):
    def first_pass(self, parser, node, nodes):
        print "Evaluating position"
        return reduce(lambda x, y: (x[0]+y[0], x[1]+y[1]), nodes[1:-2])

# Connecting rules with semantic actions
program.sem = Program()
command.sem = Command()
up.sem = Up()
down.sem = Down()
left.sem = Left()
right.sem = Right()

if __name__ == "__main__":
    try:

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

        # Then we export it to a dot file in order to visualize it. This is
        # particularly handy for debugging purposes.
        # We can make a jpg out of it using dot (part of graphviz) like this
        # dot -O -Tjpg robot_parse_tree_model.dot
        PMDOTExport().exportFile(parser.parser_model,
                        "robot_parse_tree_model.dot")

        # We create a parse tree out of textual input
        parse_tree = parser.parse(input)

        # Then we export it to a dot file in order to visualize it.
        # dot -O -Tjpg robot_parse_tree.dot
        PTDOTExport().exportFile(parse_tree,
                        "robot_parse_tree.dot")

        # getASG will start semantic analysis.
        # In this case semantic analysis will evaluate expression and
        # returned value will be the final position of the robot.
        print "position = ", parser.getASG()

    except NoMatch, e:
        print "Expected %s at position %s." % (e.value, str(e.parser.pos_to_linecol(e.position)))
