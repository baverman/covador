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


def wrap_in(key):
    return lambda val: {key: val}


def make_validator(getter, on_error, top_schema):
    def validator(*args, **kwargs):
        s = top_schema(*args, **kwargs)
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                data = getter(*args, **kwargs)
                try:
                    data = s(data)
                except Exception as e:
                    return on_error(e)
                else:
                    kwargs.update(data)
                    return func(*args, **kwargs)
            return inner
        return decorator
    return validator
