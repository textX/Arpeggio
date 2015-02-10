#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# Arpeggio is an implementation of packrat parser interpreter based on PEG grammars.
# Parsers are defined using python language construction or PEG language.
###############################################################################

__author__ = "Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>"
__version__ = "0.10"

from setuptools import setup

NAME = 'Arpeggio'
VERSION = __version__
DESC = 'Packrat parser interpreter'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor DOT dejanovic AT gmail DOT com'
LICENSE = 'MIT'
URL = 'https://github.com/igordejanovic/Arpeggio'
DOWNLOAD_URL = 'https://github.com/igordejanovic/Arpeggio/archive/v{}.tar.gz'\
    .format(VERSION)

setup(
    name = NAME,
    version = VERSION,
    description = DESC,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer = AUTHOR,
    maintainer_email = AUTHOR_EMAIL,
    license = LICENSE,
    url = URL,
    download_url = DOWNLOAD_URL,
    packages = ["arpeggio"],
    keywords = "parser packrat peg",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
        ]

)
