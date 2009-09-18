#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# Arpeggio is implementation of pacrat parser interpreter based on PEG grammars.
# Parsers are defined using python language construction or PEG language.
#######################################################################

__author__ = "Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>"
__version__ = "0.1-dev"

from setuptools import setup

NAME = 'Arpeggio'
VERSION = __version__
DESC = 'Pacrat parser interpreter'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor DOT dejanovic AT gmail DOT com'
LICENCE = 'MIT'
URL = 'http://arpeggio.googlecode.com/'

setup(
    name = NAME,
    version = VERSION,
    description = DESC,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer = AUTHOR,
    maintainer_email = AUTHOR_EMAIL,
    license = LICENCE,
    url = URL,
    packages = ["arpeggio"],
    keywords = "parser pacrat peg",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules'
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]

)
