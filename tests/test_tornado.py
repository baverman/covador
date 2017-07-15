# -*- coding: utf-8 -*-
import json

from tornado import web
from tornado.httputil import HTTPServerRequest

from covador import item, wrap_in, dpass
from covador.tornado import query_string, form, json_body, rparams, params

app = web.Application()


class Connection:
    def __init__(self):
        self.data = b''

    def set_close_callback(self, cb):
        pass

    def write_headers(self, sline, headers, chunk, callback):
        self.code = sline.code
        self.data += chunk

    def finish(self):
        pass


def test_query_string():
    class Handler(web.RequestHandler):
        @dpass(query_string(boo='bytes') | wrap_in('raw'))
        @query_string(boo=str, _=wrap_in('data'))
        def get(self, data, raw):
            return data, raw

    request = HTTPServerRequest('GET', '/?boo=boo', connection=Connection())
    h = Handler(app, request)
    data, raw = h.get()
    assert repr(data['boo']) == repr(u'boo')
    assert repr(raw['boo']) == repr(b'boo')


def test_form():
    class Handler(web.RequestHandler):
        @form(boo=str, raw_boo=item('bytes', src='boo'))
        def post(self, boo, raw_boo):
            return boo, raw_boo

    request = HTTPServerRequest('POST', '/', body=b'boo=boo', connection=Connection())
    h = Handler(app, request)
    data, raw = h.post()
    assert repr(data) == repr(u'boo')
    assert repr(raw) == repr(b'boo')


def test_json():
    class Handler(web.RequestHandler):
        @json_body(foo=str)
        def post(self, foo):
            return foo

    data = u'{"foo": "утф"}'.encode('utf-8')
    request = HTTPServerRequest('POST', '/', body=data, connection=Connection())
    h = Handler(app, request)
    data = h.post()
    assert data == u'утф'


def test_params():
    class Handler(web.RequestHandler):
        @params(boo=str, foo=int)
        def post(self, boo, foo):
            return boo, foo

    request = HTTPServerRequest('POST', '/?boo=boo', body=b'foo=10', connection=Connection())
    h = Handler(app, request)
    boo, foo = h.post()
    assert boo, foo == (u'boo', 10)


def test_rparams():
    class Handler(web.RequestHandler):
        @rparams(boo=int)
        def post(self, boo):
            return boo

    request = HTTPServerRequest('POST', '/?boo=boo', body=b'foo=10', connection=Connection())
    h = Handler(app, request)
    assert h.post(boo='20') == 20


def test_error():
    class Handler(web.RequestHandler):
        @query_string(boo=int)
        def get(self, boo):
            return 'ok'

    conn = Connection()
    request = HTTPServerRequest('GET', '/', connection=conn)
    h = Handler(app, request)
    h._transforms = [t(request) for t in app.transforms]
    assert h.get() == None
    assert conn.code == 400

    error = json.loads(conn.data.decode('utf-8'))
    assert error == {'details': {'boo': 'Required item'},
                     'error': 'bad-request'}
