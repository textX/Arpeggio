# proj
from . import parser_base
from . import parser_python
from . import peg_expressions
from . import peg_lexical
from . import visitor_base
from . import visitor_peg


__all__ = ['ParserPEG']


def rule():
    return peg_lexical.rule_name, peg_lexical.LEFT_ARROW, peg_lexical.ordered_choice, ";"


# PEG syntax rules
def peggrammar():
    return peg_expressions.OneOrMore(rule), peg_expressions.EOF


class ParserPEG(parser_base.Parser):

    def __init__(self, language_def, root_rule_name, comment_rule_name=None, *args, **kwargs):
        """
        Constructs parser from textual PEG definition.

        Args:
            language_def (str): A string describing language grammar using
                PEG notation.
            root_rule_name(str): The name of the root rule.
            comment_rule_name(str): The name of the rule for comments.
        """
        super().__init__(*args, **kwargs)
        self.root_rule_name = root_rule_name
        self.comment_rule_name = comment_rule_name

        # PEG Abstract Syntax Graph
        self.parser_model, self.comments_model = self._from_peg(language_def)
        # Comments should be optional and there can be more of them
        if self.comments_model:
            self.comments_model.root = True
            self.comments_model.rule_name = comment_rule_name

        # In debug mode export parser model to dot for
        # visualization
        if self.debug:
            try:
                # for pytest
                from .export import PMDOTExporter   # type: ignore # pragma: no cover
            except ImportError:                     # type: ignore # pragma: no cover
                # for local Doctest                 # type: ignore # pragma: no cover
                from export import PMDOTExporter    # type: ignore # pragma: no cover

            root_rule = self.parser_model.rule_name
            PMDOTExporter().exportFile(
                self.parser_model, "{}_peg_parser_model.dot".format(root_rule))

    def _parse(self):
        return self.parser_model.parse(self)

    def _from_peg(self, language_def):
        parser = parser_python.ParserPython(peggrammar, peg_lexical.comment, reduce_tree=False, debug=self.debug)
        parser.root_rule_name = self.root_rule_name
        parse_tree = parser.parse(language_def)

        return visitor_base.visit_parse_tree(parse_tree, visitor_peg.PEGVisitor(self.root_rule_name,
                                                                                self.comment_rule_name,
                                                                                self.ignore_case,
                                                                                debug=self.debug))
