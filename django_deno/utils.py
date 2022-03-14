import collections
import traceback


def ex_to_str(ex):
    return '\n'.join(
        list(traceback.TracebackException.from_exception(ex).format())
    )


def unfold(iterable, max_level=None, curr_level=1):
    ret = []
    for element in iterable:
        if isinstance(element, collections.Iterable) and (max_level is None or curr_level < max_level):
            ret.append(unfold(element, max_level=max_level, curr_level=curr_level + 1))
        else:
            ret.append(element)
    return ret
