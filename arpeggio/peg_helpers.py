from .peg_nodes import NonTerminal


def flatten(_iterable):
    """ Flattening of python iterables."""
    result = []
    for e in _iterable:
        if hasattr(e, "__iter__") and not type(e) in [str, NonTerminal]:
            result.extend(flatten(e))
        else:
            result.append(e)
    return result
