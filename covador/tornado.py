from __future__ import absolute_import
import json

from functools import wraps
from . import list_schema, schema, ValidationDecorator
from .errors import error_to_json
from .utils import ErrorHandler, parse_qs, merge_dicts
from .compat import ustr


def error_adapter(func):
    @wraps(func)
    def inner(ctx):
        return func(ctx.args[0], ctx)
    return inner


@ErrorHandler
@error_adapter
def error_handler(handler, ctx):
    handler.set_status(400)
    handler.finish(error_to_json(ctx.exception))


def get_form(request):
    try:
        return request._covador_form
    except AttributeError:
        result = request._covador_form = parse_qs(request.body)
        return result


def get_json(request):
    try:
        return request._covador_json
    except AttributeError:
        result = request._covador_json = json.loads(ustr(request.body, 'utf-8'))
        return result


_query_string = lambda self, *_args, **_kwargs: self.request.query_arguments
_form = lambda self, *_args, **_kwargs: get_form(self.request)
_params = lambda self, *_args, **_kwargs: merge_dicts(self.request.arguments, get_form(self.request))
_rparams = lambda *_args, **kwargs: kwargs
_json_body = lambda self, *_args, **_kwargs: get_json(self.request)

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = ValidationDecorator(_params, error_handler, list_schema)
rparams = ValidationDecorator(_rparams, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema)
