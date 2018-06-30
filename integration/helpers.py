# -*- coding: utf-8 -*-
import random
import string

from covador.compat import bstr

_BOUNDARY_CHARS = string.digits + string.ascii_letters


def encode_multipart(fields, boundary=None):
    def escape_quote(s):
        return bstr(s).replace(b'"', b'\\"')

    if boundary is None:
        boundary = ''.join(random.choice(_BOUNDARY_CHARS) for i in range(30)).encode('latin1')
    lines = []

    for name, value in fields:
        lines.extend((
            b'--' + boundary,
            u'Content-Disposition: form-data; name="{0}"'.format(
                escape_quote(name).decode('latin1')).encode('latin1'),
            b'',
            bstr(value, 'utf-8'),
        ))

    lines.extend((
        b'--' + boundary + b'--',
        b'',
    ))
    body = b'\r\n'.join(lines)
    return (body, 'multipart/form-data; boundary={0}'.format(boundary.decode('latin1')))


mform, mct = encode_multipart([('p1', u'буу'), ('p2', '10')])
