from __future__ import absolute_import
import json
from functools import wraps

from . import list_schema, schema
from .compat import ustr
from .errors import error_to_json
from .utils import parse_qs
from .vdecorator import ValidationDecorator, ErrorHandler, mergeof


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
        content_type = request.headers.get('Content-Type', '')
        if content_type.startswith('multipart/form-data'):
            result = request.body_arguments
        elif content_type.startswith('application/x-www-form-urlencoded'):
            result = parse_qs(request.body)
        else:
            result = {}
        request._covador_form = result
        return result


def get_json(request):
    try:
        return request._covador_json
    except AttributeError:
        content_type = request.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            result = json.loads(ustr(request.body, 'utf-8'))
        else:
            result = {}
        request._covador_json = result
        return result


_query_string = lambda self, *_args, **_kwargs: self.request.query_arguments
_form = lambda self, *_args, **_kwargs: get_form(self.request)
_args = lambda *_args, **kwargs: kwargs
_json_body = lambda self, *_args, **_kwargs: get_json(self.request)

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = mergeof(query_string, form)
args = ValidationDecorator(_args, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema)
