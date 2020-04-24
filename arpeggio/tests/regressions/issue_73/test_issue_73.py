from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, UnorderedGroup, Optional, \
    EOF, NoMatch


def test_nondeterministic_unordered_group():

    def root():
        return 'word1', UnorderedGroup(some_rule, 'word2', some_rule), EOF

    def some_rule():
        return Optional('word2'), Optional('word3')

    content = '''word1 word2 '''

    # If the 'word2' from unordered group in the `root` rule matches first
    # the input parses, else it fails.
    # We repeat parser construction and parsing many times to check
    # if it fails every time. The current fix will iterate in order from left
    # to right and repeat matching until all rules in a unordered group
    # succeeds.
    fail = 0
    success = 0
    for _ in range(100):
        try:
            parser = ParserPython(root)
            parser.parse(content)
            success += 1
        except NoMatch:
            fail += 1

    assert fail == 100
