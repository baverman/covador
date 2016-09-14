from __future__ import absolute_import

from django import http
from . import ListMap, make_schema, make_validator
from .utils import merge_dicts, parse_qs


def on_error(exc):  # pragma: no cover
    return http.HttpResponseBadRequest(str(exc))


def get_qs(request):
    try:
        return request._covador_qs
    except AttributeError:
        qs = request._covador_qs = parse_qs(request.environ.get('QUERY_STRING', ''))
        return qs


def get_form(request):
    try:
        return request._covador_form
    except AttributeError:
        form = request._covador_form = parse_qs(request.body)
        return form


schema = make_schema(ListMap)
_query_string = lambda request, *_args, **_kwargs: get_qs(request)
_form = lambda request, *_args, **_kwargs: get_form(request)
_params = lambda request, *_args, **_kwargs: merge_dicts(get_qs(request), get_form(request))
_rparams = lambda *_args, **kwargs: kwargs

query_string = make_validator(_query_string, on_error, schema)
form = make_validator(_form, on_error, schema)
params = make_validator(_params, on_error, schema)
rparams = make_validator(_rparams, on_error, schema)

m_query_string = make_validator(_query_string, on_error, schema, 1)
m_form = make_validator(_form, on_error, schema, 1)
m_params = make_validator(_params, on_error, schema, 1)
m_rparams = make_validator(_rparams, on_error, schema, 1)
