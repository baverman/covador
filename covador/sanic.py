from __future__ import absolute_import

from sanic import response
from . import ValidationDecorator, schema, list_schema
from .utils import merge_dicts, ErrorHandler
from .errors import error_to_json


@ErrorHandler
def error_handler(ctx):
    return response.json(error_to_json(ctx.exception), status=400)


_query_string = lambda request, *_args, **_kwargs: request.args
_form = lambda request, *_args, **_kwargs: request.form
_params = lambda request, *_args, **_kwargs: merge_dicts(request.args, request.form)
_rparams = lambda request, *_args, **kwargs: kwargs
_json = lambda request, *_args, **_kwargs: request.json

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = ValidationDecorator(_params, error_handler, list_schema)
rparams = ValidationDecorator(_rparams, error_handler, schema)
json_body = ValidationDecorator(_json, error_handler, schema)
