# stdlib
import abc
import sys


class DebugPrinter(abc.ABC):
    """
    Mixin Metaclass for adding debug print support.

    Attributes:
        debug (bool): If true debugging messages will be printed.
        _current_ident(int): Current indention level for prints.
    """

    def __init__(self, **kwargs) -> None:

        self.debug = kwargs.pop("debug", False)
        self.file = kwargs.pop("file", sys.stdout)
        self._current_ident = 0

    def dprint(self, message, ident_change=0):
        """
        Handle debug message. Print to the stream specified by the 'file'
        keyword argument at the current indentation level. Default stream is
        stdout.
        """
        if ident_change < 0:
            self._current_ident += ident_change

        print(("%s%s" % ("   " * self._current_ident, message)),
              file=self.file)

        if ident_change > 0:
            self._current_ident += ident_change


class CrossRef(object):
    """ Used for rule reference resolving.
    """
    def __init__(self, target_rule_name, position=-1):
        self.target_rule_name = target_rule_name
        self.position = position
