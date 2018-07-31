from functools import wraps, partial
from asyncio import coroutine

from aiohttp.web import HTTPBadRequest

from . import schema, list_schema
from .types import make_schema, AltMap
from .utils import parse_qs
from .vdecorator import ValidationDecorator, Validator, ErrorHandler, ErrorContext
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

        inner.schema = self.schema
        return inner


def mergeof(*vdecorators):
    first = vdecorators[0]

    getters = [r.getter if isinstance(r.validator, AsyncValidator) else coroutine(r.getter)
               for r in vdecorators]
    schemas = [r.top_schema.schema for r in vdecorators]

    @coroutine
    def getter(*args, **kwargs):
        return [(yield from g(*args, **kwargs)) for g in getters]

    top_schema = make_schema(partial(AltMap, schemas))

    return ValidationDecorator(getter, first.error_handler, top_schema, first.skip_args, AsyncValidator)


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


def listdict(mdict):
    result = {}
    for k, v in mdict.items():
        result.setdefault(k, []).append(v)
    return result


@coroutine
def get_form(request):
    try:
        return request._covador_form
    except AttributeError:
        if request.content_type.startswith('multipart/form-data'):
            form = listdict((yield from request.post()))
        elif request.content_type.startswith('application/x-www-form-urlencoded'):
            form = parse_qs((yield from request.read()))
        else:
            form = {}
        form = request._covador_form = form
        return form


@coroutine
def get_json(request):
    if request.content_type.startswith('application/json'):
        return (yield from request.json())
    return {}


_query_string = lambda request, *_args, **_kwargs: get_qs(get_request(request))
_form = lambda request, *_args, **_kwargs: get_form(get_request(request))
_args = lambda request, *_args, **_kwargs: get_request(request).match_info
_json_body = lambda request, *_args, **_kwargs: get_json(get_request(request))

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema, validator=AsyncValidator)
params = mergeof(query_string, form)
args = ValidationDecorator(_args, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema, validator=AsyncValidator)
