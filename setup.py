#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2017 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# Arpeggio is an implementation of packrat parser interpreter based on PEG
# grammars.
# Parsers are defined using python language construction or PEG language.
###############################################################################

import codecs
import os
import sys
from setuptools import setup

VERSIONFILE = "arpeggio/__init__.py"
VERSION = None
for line in codecs.open(VERSIONFILE, "r", encoding='utf-8').readlines():
    if line.startswith('__version__'):
        VERSION = line.split('"')[1]

if not VERSION:
    raise RuntimeError('No version defined in arpeggio/__init__.py')

NAME = 'Arpeggio'
DESC = 'Packrat parser interpreter'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor.dejanovic@gmail.com'
LICENSE = 'MIT'
URL = 'https://github.com/igordejanovic/Arpeggio'
DOWNLOAD_URL = 'https://github.com/igordejanovic/Arpeggio/archive/v{}.tar.gz'\
    .format(VERSION)

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

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=["arpeggio"],
    keywords="parser packrat peg",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
