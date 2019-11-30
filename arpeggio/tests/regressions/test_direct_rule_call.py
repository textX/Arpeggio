# stdlib
from typing import Any

# proj
try:
    # imports for local pytest
    from ...arpeggio import ParserPython                    # type: ignore # pragma: no cover
    from ...peg_semantic_actions import SemanticAction      # type: ignore # pragma: no cover
except ImportError:                                         # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    from arpeggio import ParserPython                       # type: ignore # pragma: no cover
    from peg_semantic_actions import SemanticAction         # type: ignore # pragma: no cover


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
        def first_pass(self, parser, node, nodes):
            call_count[0] += 1
            return SemanticAction.first_pass(self, parser, node, nodes)

    # Sem action is attached to rule2 only but
    # this bug will attach it to rule1 also resulting in
    # wrong call count.
    rule2.sem = DummySemAction()        # type: ignore

    parser = ParserPython(grammar)
    parse_tree = parser.parse("aa")
    parser.getASG()

    assert call_count[0] == 1, "Semantic action should be called once!"
