# proj
try:
    # imports for local pytest
    from .arpeggio import *                  # type: ignore # pragma: no cover
    from .peg_lexical import *               # type: ignore # pragma: no cover
    from .visitor_peg import *               # type: ignore # pragma: no cover
    from .parser_base import Parser          # type: ignore # pragma: no cover
    from .parser_python import ParserPython  # type: ignore # pragma: no cover
except ImportError:                          # type: ignore # pragma: no cover
    from arpeggio import *                   # type: ignore # pragma: no cover
    from peg_lexical import *                # type: ignore # pragma: no cover
    from visitor_peg import *                # type: ignore # pragma: no cover
    from parser_base import Parser           # type: ignore # pragma: no cover
    from parser_python import ParserPython   # type: ignore # pragma: no cover

__all__ = ['ParserPEG']


def rule():
    return rule_name, LEFT_ARROW, ordered_choice, ";"


# PEG syntax rules
def peggrammar():
    return OneOrMore(rule), EOF


class ParserPEG(Parser):

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
        parser = ParserPython(peggrammar, comment, reduce_tree=False,
                              debug=self.debug)
        parser.root_rule_name = self.root_rule_name
        parse_tree = parser.parse(language_def)

        return visit_parse_tree(parse_tree, PEGVisitor(self.root_rule_name,
                                                       self.comment_rule_name,
                                                       self.ignore_case,
                                                       debug=self.debug))
