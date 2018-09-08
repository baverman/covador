import os
import sys
import logging
from functools import wraps

from .compat import reraise
from .utils import clone
from .types import make_schema, pipe

DEBUG = os.environ.get('COVADOR_DEBUG')
log = logging.getLogger('covador.bad-request')


class ErrorContext(object):
    def __init__(self, args=None, kwargs=None, exc_info=None):
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.exc_info = exc_info or sys.exc_info()
        if DEBUG:  # pragma: no cover
            log.error('Bad request: %r', self.exc_info[1], exc_info=self.exc_info)
        else:
            log.info('Bad request: %r', self.exc_info[1])

    def reraise(self, exception=None):
        if exception:
            reraise(type(exception), exception, self.exc_info[2])
        else:
            reraise(self.exc_info[0], self.exc_info[1], self.exc_info[2])

    @property
    def exception(self):
        return self.exc_info[1]


class AltItemGetter(object):
    def __init__(self, item_getters):
        self.item_getters = [it.get for it in item_getters]
        self.item_to_dict = [it.to_dict for it in item_getters]

    def get(self, data, item):
        for d, fn in zip(data, self.item_getters):
            if item.src in d:
                return fn(d, item)

    def to_dict(self, data, multi=False):
        result = {}
        for d, fn in zip(data, self.item_to_dict):
            result.update(fn(d, multi))
        return result


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

        inner.schema = self.schema
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


def mergeof(*vdecorators):
    first = vdecorators[0]

    getters = [r.getter for r in vdecorators]
    item_getters = [r.top_schema.item_getter for r in vdecorators]

    def getter(*args, **kwargs):
        return [g(*args, **kwargs) for g in getters]

    top_schema = make_schema(AltItemGetter(item_getters))
    return ValidationDecorator(getter, first.error_handler, top_schema, first.skip_args)


class ErrorHandler(object):
    def __init__(self, default):
        self.default = default
        self.handler = None

    def __call__(self, ctx):
        return (self.handler or self.default)(ctx)

    def set(self, handler):
        self.handler = handler
