"""
Various utilities.
"""

# isstr check if object is of string type.
# This works for both python 2 and 3
# Taken from http://stackoverflow.com/questions/11301138/how-to-check-if-variable-is-string-with-python-2-and-3-compatibility
try:
    str  # attempt to evaluate basestring
    def isstr(s):
        return isinstance(s, str)
except NameError:
    def isstr(s):
        return isinstance(s, str)