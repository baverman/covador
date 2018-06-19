from __future__ import absolute_import
from functools import wraps
import json
import cgi

from django import http

from . import list_schema, schema
from .utils import parse_qs
from .vdecorator import ValidationDecorator, ErrorHandler, mergeof
from .errors import error_to_json
from .compat import ustr


def error_adapter(func):
    @wraps(func)
    def inner(ctx):
        return func(ctx.args[0], ctx)
    return inner


@ErrorHandler
@error_adapter
def error_handler(_request, ctx):
    return http.HttpResponseBadRequest(error_to_json(ctx.exception))


def get_qs(request):
    try:
        return request._covador_qs
    except AttributeError:
        qs = request._covador_qs = parse_qs(request.environ.get('QUERY_STRING', ''))
        return qs


def get_content_type(request):
    try:
        content_type = request.content_type
    except AttributeError:  # pragma: no cover
        content_type, _ = cgi.parse_header(
            request.META.get('CONTENT_TYPE', ''))
    return content_type


def get_form(request):
    try:
        return request._covador_form
    except AttributeError:
        content_type = get_content_type(request)
        if content_type.startswith('multipart/form-data'):
            form = dict(request.POST.lists())
        elif content_type.startswith('application/x-www-form-urlencoded'):
            form = parse_qs(request.body)
        else:
            form = {}
        form = request._covador_form = form
        return form


def get_json(request):
    if get_content_type(request).startswith('application/json'):
        return json.loads(ustr(request.body, request.encoding or 'utf-8'))
    return {}


_query_string = lambda request, *_args, **_kwargs: get_qs(request)
_form = lambda request, *_args, **_kwargs: get_form(request)
_args = lambda *_args, **kwargs: kwargs
_json_body = lambda request, *_args, **_kwargs: get_json(request)

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = mergeof(query_string, form)
args = ValidationDecorator(_args, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema)

m_query_string = ValidationDecorator(_query_string, error_handler, list_schema, 1)
m_form = ValidationDecorator(_form, error_handler, list_schema, 1)
m_params = mergeof(m_query_string, m_form)
m_args = ValidationDecorator(_args, error_handler, schema, 1)
m_json_body = ValidationDecorator(_json_body, error_handler, schema, 1)
