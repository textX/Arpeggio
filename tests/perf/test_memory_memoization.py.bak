#-*- coding: utf-8 -*-
#######################################################################
# Purpose: Testing memory consumption with memoization enabled.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import print_function, unicode_literals

import codecs
from os.path import dirname, join
from memory_profiler import profile
from arpeggio import ParserPython
from grammar import rhapsody

@profile
def memoization():

    parser = ParserPython(rhapsody, memoization=True)

    # Smaller file
    file_name = join(dirname(__file__), 'test_inputs', 'LightSwitch.rpy')
    with codecs.open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    small = parser.parse(content)

    # File that is double in size
    file_name = join(dirname(__file__), 'test_inputs', 'LightSwitchDouble.rpy')
    with codecs.open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    large = parser.parse(content)

if __name__ == '__main__':
    memoization()
