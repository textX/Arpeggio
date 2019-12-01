from .peg_nodes import Terminal
from .peg_utils import *


class PTNodeVisitor(DebugPrinter):
    """
    Base class for all parse tree visitors.
    """
    def __init__(self, defaults=True, **kwargs):
        """
        Args:
            defaults(bool): If the default visit method should be applied in
                case no method is defined.
        """
        self.for_second_pass = []
        self.defaults = defaults

        super(PTNodeVisitor, self).__init__(**kwargs)

    def visit__default__(self, node, children):
        """
        Called if no visit method is defined for the node.

        Args:
            node(ParseTreeNode):
            children(processed children ParseTreeNode-s):
        """
        if isinstance(node, Terminal):
            # Default for Terminal is to convert to string unless suppress flag
            # is set in which case it is suppressed by setting to None.
            retval = str(node) if not node.suppress else None
        else:
            retval = node
            # Special case. If only one child exist return it.
            if len(children) == 1:
                retval = children[0]
            else:
                # If there is only one non-string child return
                # that by default. This will support e.g. bracket
                # removals.
                last_non_str = None
                for c in children:
                    if not isinstance(c, str):
                        if last_non_str is None:
                            last_non_str = c
                        else:
                            # If there is multiple non-string objects
                            # by default convert non-terminal to string
                            if self.debug:
                                self.dprint("*** Warning: Multiple "
                                            "non-string objects found in "
                                            "default visit. Converting non-"
                                            "terminal to a string.")
                            retval = str(node)
                            break
                else:
                    # Return the only non-string child
                    retval = last_non_str

        return retval


def visit_parse_tree(parse_tree, visitor):
    """
    Applies visitor to parse_tree and runs the second pass
    afterwards.

    Args:
        parse_tree(ParseTreeNode):
        visitor(PTNodeVisitor):
    """
    if not parse_tree:
        raise Exception(
            "Parse tree is empty. You did call parse(), didn't you?")

    if visitor.debug:
        visitor.dprint("ASG: First pass")

    # Visit tree.
    result = parse_tree.visit(visitor)

    # Second pass
    if visitor.debug:
        visitor.dprint("ASG: Second pass")
    for sa_name, asg_node in visitor.for_second_pass:
        getattr(visitor, "second_%s" % sa_name)(asg_node)

    return result
