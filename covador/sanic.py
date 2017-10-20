from __future__ import absolute_import

from sanic import response
from . import schema, list_schema
from .vdecorator import ValidationDecorator, ErrorHandler, mergeof
from .errors import error_to_json


@ErrorHandler
def error_handler(ctx):
    return response.raw(error_to_json(ctx.exception), status=400, content_type='application/json')


def get_json(request):
    if request.content_type.startswith('application/json'):
        return request.json
    return {}


_query_string = lambda request, *_args, **_kwargs: request.args
_form = lambda request, *_args, **_kwargs: request.form
_rparams = lambda _request, *_args, **kwargs: kwargs
_json = lambda request, *_args, **_kwargs: get_json(request)

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = mergeof(query_string, form)
rparams = ValidationDecorator(_rparams, error_handler, schema)
json_body = ValidationDecorator(_json, error_handler, schema)

m_query_string = ValidationDecorator(_query_string, error_handler, list_schema, 1)
m_form = ValidationDecorator(_form, error_handler, list_schema, 1)
m_params = mergeof(m_query_string, m_form)
m_rparams = ValidationDecorator(_rparams, error_handler, schema, 1)
m_json_body = ValidationDecorator(_json, error_handler, schema, 1)
