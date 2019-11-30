# this __init__.py is only meant for local package development

# proj
try:
    # imports for local pytest
    from .arpeggio import *                                 # type: ignore # pragma: no cover
    # this we need for pip install --install-option test
except ImportError:                                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import arpeggio                                         # type: ignore # pragma: no cover
