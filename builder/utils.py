import functools
import sys


def announce_calls(announcement=None, after_call=False, bold=True):
    """
    Decorator for printing a message when called, defaulting to first line of docstring
    :param announcement: message to print
    :param after_call: announce after calling instead of before
    :param bold: whether the message should be bold
    """

    def decorator(func):
        message = announcement or one_line_doc(func) or getattr(func, '__name__', '')
        if bold and sys.stdout.isatty():
            message = term_bold(message)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            if message and not after_call:
                print(term_bold(message), file=sys.stdout)
            result = func(*args, **kwargs)
            if message and after_call:
                print(term_bold(message), file=sys.stdout)
            return result

        return wrapped_func

    return decorator


def requisites(*prerequisites):
    """
    A decorator to call pre-requisites before proceeding.
    If any return False, the chain stops.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            for requisite in prerequisites:
                result = requisite(*args, **kwargs)
                if result is False:
                    return
            return func(*args, **kwargs)

        return wrapped_func

    return decorator


def _term(message, flag):
    return '\x1b[%sm%s\x1b[0m' % (flag, message)


def term_bold(message):
    """
    Returns a bold version or message for printing to the terminal
    :param message: the message to wrap
    """
    return _term(message, '1')


def term_green(message):
    """
    Returns a green version or message for printing to the terminal
    :param message: the message to wrap
    """
    return _term(message, '32')


def term_red(message):
    """
    Returns a red version or message for printing to the terminal
    :param message: the message to wrap
    """
    return _term(message, '31')


def one_line_doc(obj):
    """
    Returns the first line of a docstring
    :param obj: an object with a docstring
    """
    doc = getattr(obj, '__doc__', None) or ''
    doc = doc.strip().splitlines()
    return doc[0] if doc else ''
