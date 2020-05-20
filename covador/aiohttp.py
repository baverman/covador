from functools import wraps

from aiohttp.web import HTTPBadRequest

from . import schema, list_schema
from .utils import parse_qs
from .autils import mark_coro
from .vdecorator import ValidationDecorator, ErrorHandler, mergeof
from .errors import error_to_json
from .ast_transformer import import_module

import_module('covador.aiohttp_t', (('fn', True),))
from .aiohttp_t import get_form, get_json


def error_adapter(func):
    @wraps(func)
    def inner(ctx):
        return func(get_request(ctx.args[0]), ctx)
    return inner


@ErrorHandler
@error_adapter
def error_handler(_request, ctx):
    raise HTTPBadRequest(body=error_to_json(ctx.exception),
                         content_type='application/json')


def get_qs(request):
    try:
        return request['_covador_qs']
    except KeyError:
        qs = request['_covador_qs'] = parse_qs(request.query_string or '')
        return qs



def get_request(obj):
    return getattr(obj, 'request', obj)


_query_string = lambda request, *_args, **_kwargs: get_qs(get_request(request))
_form = mark_coro(lambda request, *_args, **_kwargs: get_form(get_request(request)))
_args = lambda request, *_args, **_kwargs: get_request(request).match_info
_json_body = mark_coro(lambda request, *_args, **_kwargs: get_json(get_request(request)))

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = mergeof(query_string, form)
args = ValidationDecorator(_args, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema)
