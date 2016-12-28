from functools import wraps
from asyncio import coroutine

from aiohttp.web import Response

from . import ListMap, make_schema
from .utils import merge_dicts, parse_qs


def on_error(exc):  # pragma: no cover
    return Response(text=str(exc), status=400)


@coroutine
def get_qs(request):
    try:
        return request['_covador_qs']
    except KeyError:
        qs = request['_covador_qs'] = parse_qs(request.query_string or '')
        return qs


@coroutine
def get_form(request):
    try:
        return request._covador_form
    except AttributeError:
        form = request._covador_form = parse_qs((yield from request.read()))
        return form


schema = make_schema(ListMap)


def make_validator(getter, on_error, top_schema, skip_args=0):
    def validator(*args, **kwargs):
        s = top_schema(*args, **kwargs)

        def decorator(func):
            @wraps(func)
            @coroutine
            def inner(*args, **kwargs):
                data = (yield from getter(*args[skip_args:], **kwargs))
                try:
                    data = s(data)
                except Exception as e:  # pragma: no cover
                    if on_error:
                        return on_error(e)
                    else:
                        raise
                else:
                    kwargs.update(data)
                    return (yield from func(*args, **kwargs))
            return inner
        return decorator
    return validator


@coroutine
def _params(request, *_args, **_kwargs):  # pragma: no cover
    return merge_dicts((yield from get_qs(request)), (yield from get_form(request)))


_query_string = lambda request, *_args, **_kwargs: get_qs(request)
_form = lambda request, *_args, **_kwargs: get_form(request)
_rparams = lambda *_args, **kwargs: kwargs

_m_query_string = lambda self, *_args, **_kwargs: get_qs(self.request)
_m_form = lambda self, *_args, **_kwargs: get_form(self.request)
_m_rparams = lambda *_args, **kwargs: kwargs

query_string = make_validator(_query_string, on_error, schema)
form = make_validator(_form, on_error, schema)
params = make_validator(_params, on_error, schema)
rparams = make_validator(_rparams, on_error, schema)

m_query_string = make_validator(_m_query_string, on_error, schema)
m_form = make_validator(_m_form, on_error, schema)
m_params = make_validator(_m_rparams, on_error, schema)
m_rparams = make_validator(_m_rparams, on_error, schema)
