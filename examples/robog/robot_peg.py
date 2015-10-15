#######################################################################
# Name: robot_peg.py
# Purpose: Simple DSL for defining robot movement (PEG version).
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
from __future__ import print_function, unicode_literals

from arpeggio import *
from arpeggio.peg import ParserPEG

# Grammar rules
robot_grammar = '''
robot <- 'begin' (command)* 'end' EOF;
command <- UP/DOWN/LEFT/RIGHT;
UP <- 'up';
DOWN <- 'down';
LEFT <- 'left';
RIGHT <- 'right';
'''

# Semantic actions visitor
from robot import RobotVisitor


def main(debug=False):
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
    # Parser model is given in the form of PEG specification therefore we
    # are using ParserPEG class.
    parser = ParserPEG(robot_grammar, 'robot', debug=debug)

    # We create a parse tree out of textual input
    parse_tree = parser.parse(input)

    # visit_parse_tree will start semantic analysis.
    # In this case semantic analysis will evaluate expression and
    # returned value will be the final position of the robot.
    return visit_parse_tree(parse_tree, RobotVisitor(debug=debug))

if __name__ == "__main__":
    # In debug mode dot (graphviz) files for parser model
    # and parse tree will be created for visualization.
    # Checkout current folder for .dot files.
    print("position = ", main(debug=True))

