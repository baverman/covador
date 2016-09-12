from functools import wraps

from .compat import PY2, ustr, urlparse


def method(func):
    @wraps(func)
    def inner(_self, *args, **kwargs):
        return func(*args, **kwargs)
    return inner


def merge_dicts(*dicts, **kwargs):
    result = {}
    for d in dicts:
        result.update(d)
    result.update(kwargs)
    return result


def parse_qs(data):
    result = urlparse.parse_qs(data, True)
    if not PY2:
        result = {ustr(k): v for k, v in result.items()}
    return result
