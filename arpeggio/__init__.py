###############################################################################
# Name: arpeggio.py
# Purpose: PEG parser interpreter
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2009-2019 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# This is an implementation of packrat parser interpreter based on PEG
# grammars. Grammars are defined using Python language constructs or the PEG
# textual notation.
###############################################################################

from .arpeggio import *
from .parser_python_class import *

__version__ = "1.9.2"

if sys.version < '3':
    raise RuntimeError('Python 3.x required')
