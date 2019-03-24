#-*- coding: utf-8 -*-
#######################################################################
# Testing parsing speed. This is used for the purpose of testing
#   of performance gains/loses for various approaches.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import print_function, unicode_literals

import codecs
import time
from os.path import dirname, join, getsize
from arpeggio import ParserPython
from grammar import rhapsody

def timeit(parser, file_name, message):
    print(message, 'File:', file_name)
    file_name = join(dirname(__file__), 'test_inputs', file_name)
    file_size = getsize(file_name)
    print('File size: {:.2f}'.format(file_size/1000), 'KB')

    with codecs.open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    t_start = time.time()
    parser.parse(content)
    t_end = time.time()

    print('Elapsed time: {:.2f}'.format(t_end - t_start), 'sec')
    print('Speed = {:.2f}'.format(file_size/1000/(t_end - t_start)), 'KB/sec')

    if parser.memoization:
        print('Cache hits = ', parser.cache_hits)
        print('Cache misses = ', parser.cache_misses)
        print('Success ratio[%] = ',
              parser.cache_hits*100/(parser.cache_hits + parser.cache_misses))
    print()


def main():

    # Small file
    file_name_small = 'LightSwitch.rpy'
    # Large file
    file_name_large = 'LightSwitchDouble.rpy'

    # No memoization
    parser = ParserPython(rhapsody)
    print('\n*** No memoization\n')
    for i in range(3):
        timeit(parser, file_name_small,
               '{}. Small file, no memoization.'.format(i + 1))
        timeit(parser, file_name_large,
               '{}. Large file, no memoization.'.format(i + 1))

    # Memoization
    parser = ParserPython(rhapsody, memoization=True)
    print('\n*** Memoization\n')
    for i in range(3):
        timeit(parser, file_name_small,
               '{}. Small file, with memoization.'.format(i + 1))
        timeit(parser, file_name_large,
               '{}. Large file, with memoization.'.format(i + 1))

if __name__ == '__main__':
    main()
