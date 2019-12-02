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
__version__ = "1.9.2"

import sys

if sys.version < '3':
    raise RuntimeError('Python 3.x required')

try:
    # imports for local pytest
    from .arpeggio_settings import *              # type: ignore # pragma: no cover
    from .error_classes import *                  # type: ignore # pragma: no cover
    from .parser_python import ParserPython       # type: ignore # pragma: no cover
    from .peg_expressions import *                # type: ignore # pragma: no cover
    from .peg_nodes import *                      # type: ignore # pragma: no cover
    from .peg_semantic_actions import *           # type: ignore # pragma: no cover
    from .visitor_base import *                   # type: ignore # pragma: no cover
except ImportError:                               # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio_settings import *               # type: ignore # pragma: no cover
    from error_classes import *                   # type: ignore # pragma: no cover
    from parser_python import ParserPython        # type: ignore # pragma: no cover
    from peg_expressions import *                 # type: ignore # pragma: no cover
    from peg_nodes import *                       # type: ignore # pragma: no cover
    from peg_semantic_actions import *            # type: ignore # pragma: no cover
    from visitor_base import *                    # type: ignore # pragma: no cover
