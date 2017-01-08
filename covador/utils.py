import sys
from functools import wraps

from .compat import PY2, ustr, urlparse, reraise


def merge_dicts(*dicts, **kwargs):
    result = {}
    for d in dicts:
        result.update(d)
    result.update(kwargs)
    return result


def parse_qs(data):
    result = urlparse.parse_qs(data, True)
    if not PY2:  # pragma: no cover py2
        result = {ustr(k): v for k, v in result.items()}
    return result


def clone(src, **kwargs):
    obj = object.__new__(type(src))
    obj.__dict__.update(src.__dict__)
    obj.__dict__.update(kwargs)
    return obj


def wrap_in(key):
    return lambda val: {key: val}


class Pipeable(object):
    def __or__(self, other):
        return Pipe([self, other])

    def __ror__(self, other):
        return Pipe([other, self])


class Pipe(Pipeable):
    def __init__(self, pipe):
        self.pipe = pipe

    def __call__(self, data):
        for it in self.pipe:
            data = it(data)
        return data

    def __or__(self, other):
        return Pipe(self.pipe + [other])

    def __ror__(self, other):
        return Pipe([other] + self.pipe)


def pipe(p1, p2):
    if isinstance(p1, Pipeable) or isinstance(p2, Pipeable):
        return p1 | p2
    return Pipe([p1, p2])


def make_schema(top_schema):
    def schema(*args, **kwargs):
        if args:
            if len(args) == 1 and not kwargs:
                return args[0]
            return top_schema(merge_dicts(*args, **kwargs))
        return top_schema(kwargs)
    return schema


class ErrorContext(object):
    def __init__(self, args=None, kwargs=None, exc_info=None):
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.exc_info = exc_info or sys.exc_info()

    def reraise(self, exception=None):
        if exception:
            reraise(type(exception), exception, self.exc_info[2])
        else:
            reraise(self.exc_info[0], self.exc_info[1], self.exc_info[2])

    @property
    def exception(self):
        return self.exc_info[1]


class Validator(object):
    def __init__(self, schema, getter, error_handler, skip_args):
        self.schema = schema
        self.getter = getter
        self.error_handler = error_handler
        self.skip_args = skip_args

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            sargs = args[self.skip_args:]
            try:
                data = self.getter(*sargs, **kwargs)
                data = self.schema(data)
            except Exception:
                if self.error_handler:
                    return self.error_handler(ErrorContext(sargs, kwargs))
                else:
                    raise
            else:
                kwargs.update(data)
                return func(*args, **kwargs)
        return inner

    def __or__(self, other):
        return clone(self, schema=pipe(self.schema, other))


class ValidationDecorator(object):
    def __init__(self, getter, error_handler, top_schema, skip_args=0, validator=None):
        self.getter = getter
        self.top_schema = top_schema
        self.skip_args = skip_args
        self.error_handler = error_handler
        self.validator = validator or Validator

    def __call__(self, *args, **kwargs):
        return self.validator(self.top_schema(*args, **kwargs), self.getter,
                              self.error_handler, self.skip_args)

    def on_error(self, handler):
        return clone(self, error_handler=handler)
