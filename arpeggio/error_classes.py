class ArpeggioError(Exception):
    """
    Base class for arpeggio errors.
    """
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)


class GrammarError(ArpeggioError):
    """
    Error raised during parser building phase used to indicate error in the
    grammar definition.
    """


class SemanticError(ArpeggioError):
    """
    Error raised during the phase of semantic analysis used to indicate
    semantic error.
    """
