'''
Created on Jul 6, 2014

@author: igor
'''
import unittest
from arpeggio import SemanticAction, ParserPython


class Test(unittest.TestCase):

    def test_direct_rule_call(self):
        '''
        Test regression where in direct rule call semantic action is
        erroneously attached to both caller and callee.
        '''

        def grammar():  return rule1, rule2
        def rule1():    return "a"
        def rule2():    return rule1

        call_count = [0]

        class DummySemAction(SemanticAction):
            def first_pass(self, parser, node, nodes):
                call_count[0] += 1
                return SemanticAction.first_pass(self, parser, node, nodes)

        # Sem action is attached to rule2 only but
        # this bug will attach it to rule1 also resulting in
        # wrong call count.
        rule2.sem = DummySemAction()

        parser = ParserPython(grammar)
        parse_tree = parser.parse("aa")
        parser.getASG()

        self.assertEqual(call_count[0], 1,
                         "Semantic action should be called once!")
