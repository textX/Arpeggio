# proj
try:
    # imports for local pytest
    from .arpeggio import Terminal   # type: ignore # pragma: no cover
except ImportError:                  # type: ignore # pragma: no cover
    from arpeggio import Terminal    # type: ignore # pragma: no cover


class SemanticAction(object):
    """
    Semantic actions are executed during semantic analysis. They are in charge
    of producing Abstract Semantic Graph (ASG) out of the parse tree.
    Every non-terminal and terminal can have semantic action defined which will
    be triggered during semantic analysis.
    Semantic action triggering is separated in two passes. first_pass method is
    required and the method called second_pass is optional and will be called
    if exists after the first pass. Second pass can be used for forward
    referencing, e.g. linking to the declaration registered in the first pass
    stage.
    """
    def first_pass(self, parser, node, nodes):
        """
        Called in the first pass of tree walk.
        This is the default implementation used if no semantic action is
        defined.
        """
        if isinstance(node, Terminal):
            # Default for Terminal is to convert to string unless suppress flag
            # is set in which case it is suppressed by setting to None.
            retval = str(node) if not node.suppress else None
        else:
            retval = node
            # Special case. If only one child exist return it.
            if len(nodes) == 1:
                retval = nodes[0]
            else:
                # If there is only one non-string child return
                # that by default. This will support e.g. bracket
                # removals.
                last_non_str = None
                for c in nodes:
                    if not isinstance(c, str):
                        if last_non_str is None:
                            last_non_str = c
                        else:
                            # If there is multiple non-string objects
                            # by default convert non-terminal to string
                            if parser.debug:
                                parser.dprint(
                                    "*** Warning: Multiple non-"
                                    "string objects found in applying "
                                    "default semantic action. Converting "
                                    "non-terminal to string.")
                            retval = str(node)
                            break
                else:
                    # Return the only non-string child
                    retval = last_non_str

        return retval


# Common semantic actions
class SemanticActionSingleChild(SemanticAction):
    def first_pass(self, parser, node, children):
        return children[0]


class SemanticActionBodyWithBraces(SemanticAction):
    def first_pass(self, parser, node, children):
        return children[1:-1]


class SemanticActionToString(SemanticAction):
    def first_pass(self, parser, node, children):
        return str(node)
