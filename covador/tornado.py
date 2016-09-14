from __future__ import absolute_import

from tornado import web
from . import ListMap, make_schema, make_validator


def on_error(exc):  # pragma: no cover
    raise web.HTTPError(400, reason=str(exc))


schema = make_schema(ListMap)
_query_string = lambda self, *_args, **_kwargs: self.request.query_arguments
_form = lambda self, *_args, **_kwargs: self.request.body_arguments
_params = lambda self, *_args, **_kwargs: self.request.arguments
_rparams = lambda *_args, **kwargs: kwargs

query_string = make_validator(_query_string, on_error, schema)
form = make_validator(_form, on_error, schema)
params = make_validator(_params, on_error, schema)
rparams = make_validator(_rparams, on_error, schema)
