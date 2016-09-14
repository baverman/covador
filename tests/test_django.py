import sys

class django:
    class http:
        class HttpResponseBadRequest(Exception):
            pass

sys.modules['django'] = django
sys.modules['django.http'] = django.http

from covador.django import *


def test_get_qs():
    class request:
        environ = {'QUERY_STRING': b'boo='}

    assert repr(get_qs(request)) == repr({'boo': [b'']})
    assert request._covador_qs


def test_get_form():
    class request:
        body = b'boo='

    assert repr(get_form(request)) == repr({'boo': [b'']})
    assert request._covador_form
