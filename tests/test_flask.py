import sys

class flask:
    class request:
        pass

class werkzeug:
    class exceptions:
        class BadRequest(Exception):
            pass

sys.modules['flask'] = flask
sys.modules['werkzeug'] = werkzeug
sys.modules['werkzeug.exceptions'] = werkzeug.exceptions

from covador.flask import *


def test_get_qs():
    request.environ = {'QUERY_STRING': b'boo='}
    assert repr(get_qs()) == repr({'boo': [b'']})
    assert request._covador_qs


def test_get_form():
    request.get_data = staticmethod(lambda *args, **kwargs: b'boo=')
    assert repr(get_form()) == repr({'boo': [b'']})
    assert request._covador_form
