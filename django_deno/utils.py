import traceback


def ex_to_str(ex):
    return '\n'.join(
        list(traceback.TracebackException.from_exception(ex).format())
    )
