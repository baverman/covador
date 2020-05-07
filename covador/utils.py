from functools import partial

from .compat import PY2, ustr, bstr, urlparse


def merge_dicts(*dicts, **kwargs):
    """Merges dicts and kwargs into one dict"""
    result = {}
    for d in dicts:
        result.update(d)
    result.update(kwargs)
    return result


def parse_qs(qs):
    """Helper func to parse query string with py2/py3 compatibility

    Ensures that dict keys are native strings.
    """
    result = {}
    qs = bstr(qs, 'latin1')
    pairs = [s2 for s1 in qs.split(b'&') for s2 in s1.split(b';')]
    uq = urlparse.unquote if PY2 else urlparse.unquote_to_bytes
    for name_value in pairs:
        if not name_value:
            continue
        nv = name_value.split(b'=', 1)
        if len(nv) != 2:
            nv.append(b'')

        name = nv[0].replace(b'+', b' ')
        name = uq(name)
        if not PY2:  # pragma: no py2 cover
            name = ustr(name, 'latin1')
        value = nv[1].replace(b'+', b' ')
        value = uq(value)
        result.setdefault(name, []).append(value)
    return result


def clone(src, **kwargs):
    """Clones object with optionally overridden fields"""
    obj = object.__new__(type(src))
    obj.__dict__.update(src.__dict__)
    obj.__dict__.update(kwargs)
    return obj


def wrap_in(key):
    """Wraps value in dict ``{key: value}``"""
    return lambda val: {key: val}


class ContexAware(object):
    def __call__(self, ctx, data):
        return data  # pragma: no cover

    def check(self, ctx):
        pass  # pragma: no cover


def ensure_context(ctx, func, right=True):
    if isinstance(func, ContexAware):  # pragma: no cover
        assert right, 'Context-aware function must be attached to right side'
        assert ctx, 'Context needed'
        func.check(ctx)
        return partial(func, ctx)
    return func


def dpass(value):
    """Allows complex inline expressions in decorator

    For example::

        @dpass(params(arg=int) | (lambda r: {'arg': r['arg'] + 10}))
        def boo(request, arg):
            pass

    Is equivalent of::

        d = params(arg=int) | (lambda r: {'arg': r['arg'] + 10})

        @d
        def boo(request, arg):
            pass
    """
    return value
