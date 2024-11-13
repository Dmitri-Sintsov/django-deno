import re
from collections.abc import Iterable
import traceback


# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
ansi_escape_8bit = re.compile(br'''
    (?: # either 7-bit C1, two bytes, ESC Fe (omitting CSI)
        \x1B
        [@-Z\\-_]
    |   # or a single 8-bit byte Fe (omitting CSI)
        [\x80-\x9A\x9C-\x9F]
    |   # or CSI + control codes
        (?: # 7-bit CSI, ESC [
            \x1B\[
        |   # 8-bit CSI, 9B
            \x9B
        )
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


def ex_to_str(ex):
    return '\n'.join(
        list(traceback.TracebackException.from_exception(ex).format())
    )


def unfold(iterable, max_level=None, curr_level=1):
    ret = []
    for element in iterable:
        if isinstance(element, Iterable) and (max_level is None or curr_level < max_level):
            ret.append(unfold(element, max_level=max_level, curr_level=curr_level + 1))
        else:
            ret.append(element)
    return ret
