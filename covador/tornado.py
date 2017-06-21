from __future__ import absolute_import
import json

from functools import wraps
from tornado import web
from . import list_schema, schema, ValidationDecorator
from .errors import error_to_json
from .utils import ErrorHandler


def error_adapter(func):  # pragma: no cover
    @wraps(func)
    def inner(ctx):
        return func(ctx.args[0], ctx)
    return inner


@ErrorHandler
@error_adapter
def error_handler(handler, ctx):  # pragma: no cover
    handler.set_status(400)
    handler.finish(error_to_json(ctx.exception))


_query_string = lambda self, *_args, **_kwargs: self.request.query_arguments
_form = lambda self, *_args, **_kwargs: self.request.body_arguments
_params = lambda self, *_args, **_kwargs: self.request.arguments
_rparams = lambda *_args, **kwargs: kwargs
_json_body = lambda self, *_args, **kwargs: json.loads(self.request.body)

query_string = ValidationDecorator(_query_string, error_handler, list_schema)
form = ValidationDecorator(_form, error_handler, list_schema)
params = ValidationDecorator(_params, error_handler, list_schema)
rparams = ValidationDecorator(_rparams, error_handler, schema)
json_body = ValidationDecorator(_json_body, error_handler, schema)
