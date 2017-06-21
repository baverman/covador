from __future__ import absolute_import
from functools import wraps
import json

from django import http

from . import ValidationDecorator, list_schema, schema
from .utils import merge_dicts, parse_qs, ErrorHandler
from .errors import error_to_json


def error_adapter(func):  # pragma: no cover
    @wraps(func)
    def inner(ctx):
        return func(ctx.args[0], ctx)
    return inner


@ErrorHandler
@error_adapter
def error_handler(_request, ctx):  # pragma: no cover
    return http.HttpResponseBadRequest(error_to_json(ctx.exception))


def get_qs(request):
    try:
        return request._covador_qs
    except AttributeError:
        qs = request._covador_qs = parse_qs(request.environ.get('QUERY_STRING', ''))
        return qs


def get_form(request):
    try:
        return request._covador_form
    except AttributeError:
        form = request._covador_form = parse_qs(request.body)
        return form


_query_string = lambda request, *_args, **_kwargs: get_qs(request)
_form = lambda request, *_args, **_kwargs: get_form(request)
_params = lambda request, *_args, **_kwargs: merge_dicts(get_qs(request), get_form(request))
_rparams = lambda *_args, **kwargs: kwargs
_json_body = lambda request, *_args, **_kwargs: json.loads(request.body)

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = ValidationDecorator(_params, error_handler, list_schema)
rparams = ValidationDecorator(_rparams, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema)

m_query_string = ValidationDecorator(_query_string, error_handler, list_schema, 1)
m_form = ValidationDecorator(_form, error_handler, list_schema, 1)
m_params = ValidationDecorator(_params, error_handler, list_schema, 1)
m_rparams = ValidationDecorator(_rparams, error_handler, schema, 1)
m_json_body = ValidationDecorator(_json_body, error_handler, schema, 1)
