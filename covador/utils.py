from functools import wraps


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
