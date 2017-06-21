import sys
from functools import wraps, partial

from .compat import PY2, ustr, urlparse, reraise


def merge_dicts(*dicts, **kwargs):
    """Merges dicts and kwargs into one dict"""
    result = {}
    for d in dicts:
        result.update(d)
    result.update(kwargs)
    return result


def parse_qs(data):
    """Helper func to parse query string with py2/py3 compatibility

    Ensures that dict keys are native strings.
    """
    result = urlparse.parse_qs(data, True)
    if not PY2:  # pragma: no cover py2
        result = {ustr(k): v for k, v in result.items()}
    return result


def clone(src, **kwargs):
    """Clones object with optionally overridden fields"""
    obj = object.__new__(type(src))
    obj.__dict__.update(src.__dict__)
    obj.__dict__.update(kwargs)
    return obj


def wrap_in(key):
    """Wraps value in dict ``{key: value}``"""
    return lambda val: {key: val}


class ContexAware(object):
    def __call__(self, ctx, data):
        return data  # pragma: no cover

    def check(self, ctx):
        pass  # pragma: no cover


def ensure_context(ctx, func, right=True):
    if isinstance(func, ContexAware):  # pragma: no cover
        assert right, 'Context-aware function must be attached to right side'
        assert ctx, 'Context needed'
        func.check(ctx)
        return partial(func, ctx)
    return func


class Pipeable(object):
    """Pipeable mixin

    Adds ``|`` operation to class.
    """
    def __or__(self, other):
        return Pipe([self, ensure_context(self, other)], self)

    def __ror__(self, other):
        return Pipe([ensure_context(self, other, False), self], self)


class Pipe(Pipeable):
    """Pipe validator

    Pass data through function list
    """
    def __init__(self, pipe, ctx=None):
        self.pipe = pipe
        self.ctx = None

    def __call__(self, data):
        for it in self.pipe:
            data = it(data)
        return data

    def __or__(self, other):
        return Pipe(self.pipe + [ensure_context(self.ctx, other)], self.ctx)

    def __ror__(self, other):
        return Pipe([ensure_context(self.ctx, other, False)] + self.pipe, self.ctx)


def pipe(p1, p2):
    """Joins two pipes"""
    if isinstance(p1, Pipeable) or isinstance(p2, Pipeable):
        return p1 | p2
    return Pipe([p1, p2])


def dpass(value):
    """Allows complex inline expressions in decorator

    For example::

        @dpass(params(arg=int) | (lambda r: {'arg': r['arg'] + 10}))
        def boo(request, arg):
            pass

    Is equivalent of::

        d = params(arg=int) | (lambda r: {'arg': r['arg'] + 10})

        @d
        def boo(request, arg):
            pass
    """
    return value


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


class ErrorHandler(object):
    def __init__(self, default):
        self.default = default
        self.handler = None

    def __call__(self, ctx):
        return (self.handler or self.default)(ctx)

    def set(self, handler):
        self.handler = handler
