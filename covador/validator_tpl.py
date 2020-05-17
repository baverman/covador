from functools import wraps
from covador.vdecorator import ErrorContext
from covador.errors import Invalid

__await__func = __await__getter = None


def gen_validator(func, schema, getter, error_handler, skip_args):
    @wraps(func)
    def inner(__async__validator, *args, **kwargs):
        sargs = args[skip_args:]
        try:
            data = __await__getter(getter(*sargs, **kwargs))
            data = schema(data)
        except Exception:
            if error_handler:
                return error_handler(ErrorContext(sargs, kwargs))
            else:
                raise
        else:
            kwargs.update(data)
            try:
                return __await__func(func(*args, **kwargs))
            except Invalid:
                if error_handler:
                    return error_handler(ErrorContext(sargs, kwargs))
                else:
                    raise

    inner.schema = schema
    return inner
