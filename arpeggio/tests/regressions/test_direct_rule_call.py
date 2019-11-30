# stdlib
from typing import Any
import pytest                                   # type: ignore

# proj

from ...arpeggio import ParserPython
from ...peg_semantic_actions import SemanticAction


def test_direct_rule_call() -> None:
    """
    Test regression where in direct rule call semantic action is
    erroneously attached to both caller and callee.
    """

    def grammar() -> Any:
        return rule1, rule2

    def rule1() -> Any:
        return "a"

    def rule2() -> Any:
        return rule1

    call_count = [0]

    class DummySemAction(SemanticAction):
        def first_pass(self, parser, node, nodes) -> SemanticAction.first_pass:
            call_count[0] += 1
            return SemanticAction.first_pass(self, parser, node, nodes)

    # Sem action is attached to rule2 only but
    # this bug will attach it to rule1 also resulting in
    # wrong call count.
    rule2.sem = DummySemAction()

    parser = ParserPython(grammar)
    parse_tree = parser.parse("aa")
    parser.getASG()

    assert call_count[0] == 1, "Semantic action should be called once!"
