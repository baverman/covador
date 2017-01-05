import sys

PY2 = sys.version_info[0] == 2

utype = type(u'')
btype = type(b'')
stype = type('')


def bstr(data, encoding='latin1'):
    if type(data) is utype:
        data = data.encode(encoding)
    return data


def ustr(data, encoding='latin1'):
    if type(data) is btype:
        data = data.decode(encoding)
    return data


if PY2:  # pragma: no cover
    import __builtin__ as builtins
    import urlparse
    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')
else:  # pragma: no cover
    import builtins
    from urllib import parse as urlparse

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
