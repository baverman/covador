from functools import wraps
from asyncio import coroutine

from aiohttp.web import Response

from . import schema, list_schema
from .utils import (merge_dicts, parse_qs, ValidationDecorator, Validator,
                    ErrorContext, ErrorHandler)
from .errors import error_to_json


class AsyncValidator(Validator):
    def __call__(self, func):
        @wraps(func)
        @coroutine
        def inner(*args, **kwargs):
            sargs = args[self.skip_args:]
            try:
                data = (yield from self.getter(*sargs, **kwargs))
                data = self.schema(data)
            except Exception:
                if self.error_handler:
                    return self.error_handler(ErrorContext(sargs, kwargs))
                else:  # pragma: no cover
                    raise
            else:
                kwargs.update(data)
                return (yield from func(*args, **kwargs))
        return inner


def error_adapter(func):
    @wraps(func)
    def inner(ctx):
        return func(get_request(ctx.args[0]), ctx)
    return inner


@ErrorHandler
@error_adapter
def error_handler(_request, ctx):
    return Response(body=error_to_json(ctx.exception), status=400,
                    content_type='application/json')


def get_qs(request):
    try:
        return request['_covador_qs']
    except KeyError:
        qs = request['_covador_qs'] = parse_qs(request.query_string or '')
        return qs


def get_request(obj):
    return getattr(obj, 'request', obj)


@coroutine
def get_form(request):
    try:
        return request._covador_form
    except AttributeError:
        form = request._covador_form = parse_qs((yield from request.read()))
        return form


@coroutine
def get_json(request):
    return (yield from request.json())


@coroutine
def _params(request, *_args, **_kwargs):
    return merge_dicts(get_qs(request), (yield from get_form(request)))


_query_string = lambda request, *_args, **_kwargs: get_qs(get_request(request))
_form = lambda request, *_args, **_kwargs: get_form(get_request(request))
_rparams = lambda *_args, **kwargs: kwargs
_json_body = lambda request, *_args, **_kwargs: get_json(get_request(request))

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema, validator=AsyncValidator)
params = ValidationDecorator(_params, error_handler, list_schema, validator=AsyncValidator)
rparams = ValidationDecorator(_rparams, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema, validator=AsyncValidator)
