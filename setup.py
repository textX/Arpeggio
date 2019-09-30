#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2019 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# Arpeggio is an implementation of packrat parser interpreter based on PEG
# grammars.
# Parsers are defined using python language construction or PEG language.
###############################################################################

import codecs
import os
import sys
from setuptools import setup, find_packages

VERSIONFILE = "arpeggio/__init__.py"
VERSION = None
for line in codecs.open(VERSIONFILE, "r", encoding='utf-8').readlines():
    if line.startswith('__version__'):
        VERSION = line.split('"')[1]

if not VERSION:
    raise RuntimeError('No version defined in arpeggio/__init__.py')

README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'),
                     'r', encoding='utf-8').read()

NAME = 'Arpeggio'
DESC = 'Packrat parser interpreter'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor.dejanovic@gmail.com'
LICENSE = 'MIT'
URL = 'https://github.com/textX/Arpeggio'
DOWNLOAD_URL = 'https://github.com/textX/Arpeggio/archive/v{}.tar.gz'\
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
    long_description=README,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite="arpeggio.tests",
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
