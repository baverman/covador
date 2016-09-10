from __future__ import absolute_import

from tornado import web
from . import ListMap, make_schema, make_validator


def on_error(exc):
    raise web.HTTPError(400, reason=exc.message)


schema = make_schema(ListMap)
_query_string = lambda self, *args, **kwargs: self.request.query_arguments
_form = lambda self, *args, **kwargs: self.request.body_arguments
_params = lambda self, *args, **kwargs: self.request.arguments

query_string = make_validator(_query_string, on_error, schema)
form = make_validator(_form, on_error, schema)
params = make_validator(_params, on_error, schema)
