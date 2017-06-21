from __future__ import absolute_import
import json

from flask import request, current_app

from . import ValidationDecorator, schema, list_schema
from .utils import merge_dicts, parse_qs, ErrorHandler
from .errors import error_to_json
from .compat import ustr


@ErrorHandler
def error_handler(ctx):  # pragma: no cover
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
        form = request._covador_form = parse_qs(request.get_data(parse_form_data=False))
        return form


_query_string = lambda *_args, **_kwargs: get_qs()
_form = lambda *_args, **_kwargs: get_form()
_params = lambda *_args, **_kwargs: merge_dicts(get_qs(), get_form())
_rparams = lambda *_args, **kwargs: kwargs
_json = lambda *_args, **_kwargs: json.loads(ustr(request.get_data(parse_form_data=False), 'utf-8'))

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = ValidationDecorator(_params, error_handler, list_schema)
rparams = ValidationDecorator(_rparams, error_handler, schema)
json_body = ValidationDecorator(_json, error_handler, schema)
