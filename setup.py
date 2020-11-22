#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# Arpeggio is an implementation of packrat parser interpreter based on PEG
# grammars.
# Parsers are defined using python language construction or PEG language.
###############################################################################

from io import open
import os
import sys
from setuptools import setup

VERSIONFILE = "arpeggio/__init__.py"
VERSION = None
for line in open(VERSIONFILE, "r", encoding='utf8').readlines():
    if line.startswith('__version__'):
        VERSION = line.split('"')[1]

if not VERSION:
    raise RuntimeError('No version defined in arpeggio/__init__.py')

if sys.argv[-1].startswith('publish'):
    if os.system("pip list | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip list | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    if sys.argv[-1] == 'publishtest':
        os.system("twine upload -r test dist/*")
    else:
        os.system("twine upload dist/*")
        print("You probably want to also tag the version now:")
        print("  git tag -a {0} -m 'version {0}'".format(VERSION))
        print("  git push --tags")
    sys.exit()

setup(version=VERSION)
