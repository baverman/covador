from __future__ import absolute_import

from flask import request
from werkzeug.exceptions import BadRequest

from . import ListMap, make_schema, make_validator, schema as sschema
from .utils import merge_dicts, parse_qs


def on_error(exc):  # pragma: no cover
    raise BadRequest(str(exc))


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


schema = make_schema(ListMap)
_query_string = lambda *_args, **_kwargs: get_qs()
_form = lambda *_args, **_kwargs: get_form()
_params = lambda *_args, **_kwargs: merge_dicts(get_qs(), get_form())
_rparams = lambda *_args, **kwargs: kwargs
_json = lambda *_args, **_kwargs: request.get_json(True)

query_string = make_validator(_query_string, on_error, schema)
form = make_validator(_form, on_error, schema)
params = make_validator(_params, on_error, schema)
rparams = make_validator(_rparams, on_error, schema)
json_body = make_validator(_json, on_error, sschema)
