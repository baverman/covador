from __future__ import absolute_import

from flask import request, current_app

from . import schema, list_schema
from .utils import parse_qs
from .vdecorator import ValidationDecorator, ErrorHandler, mergeof
from .errors import error_to_json


@ErrorHandler
def error_handler(ctx):
    return current_app.response_class(error_to_json(ctx.exception),
                                      mimetype='application/json', status=400)


def get_qs():
    try:
        return request._covador_qs
    except AttributeError:
        qs = request._covador_qs = parse_qs(request.environ.get('QUERY_STRING', ''))
        return qs


def get_form():
    try:
        return request._covador_form
    except AttributeError:
        ctype = request.content_type or ''
        if ctype.startswith('multipart/form-data'):
            form = request.form.to_dict(False)
        elif ctype.startswith('application/x-www-form-urlencoded'):
            form = parse_qs(request.get_data(parse_form_data=False))
        else:
            form = {}
        request._covador_form = form
        return form


def get_json():
    ctype = request.content_type or ''
    if ctype.startswith('application/json'):
        return request.get_json()
    return {}


_query_string = lambda *_args, **_kwargs: get_qs()
_form = lambda *_args, **_kwargs: get_form()
_args= lambda *_args, **kwargs: kwargs
_json = lambda *_args, **_kwargs: get_json()

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = mergeof(query_string, form)
args = ValidationDecorator(_args, error_handler, schema)
json_body = ValidationDecorator(_json, error_handler, schema)
