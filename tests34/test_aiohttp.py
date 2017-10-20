import json
import asyncio
import multidict
import yarl

from functools import wraps
from aiohttp import web, streams

from covador import item, opt
from covador.aiohttp import form, query_string, json_body, params, rparams

from . import helpers

FHEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


@form(boo=int)
@asyncio.coroutine
def hello_post(request, boo):
    return web.Response(text='Hello, world {}'.format(boo))


@json_body(boo=opt(int))
@asyncio.coroutine
def hello_json(request, boo):
    return web.Response(text='Hello, world {}'.format(boo or 42))


@query_string(boo=int)
@asyncio.coroutine
def hello_get(request, boo):
    return web.Response(text='Hello, world {}'.format(boo))


@rparams(foo=item(int, src='boo'))
@asyncio.coroutine
def hello_rget(request, foo):
    return web.Response(text='Hello, world {}'.format(repr(foo)))


@params(boo=int)
@asyncio.coroutine
def hello_getpost(request, boo):
    return web.Response(text='Hello, world {}'.format(boo))


class HelloView(web.View):
    @query_string(boo=int)
    @asyncio.coroutine
    def get(self, boo):
        return web.Response(text='Hello, world {}'.format(boo))

    @form(boo=int)
    @asyncio.coroutine
    def post(self, boo):
        return web.Response(text='Hello, world {}'.format(boo))


class Message:
    def __init__(self, method, path, headers):
        self.method = method
        self.path = path
        self.headers = multidict.CIMultiDict(headers)
        self.version = '1.1'
        self.url = yarl.URL(path)


class Protocol:
    transport = None


def make_request(method, path, content=None, headers=None):
    s = streams.StreamReader()
    if content is not None:
        s.feed_data(content)
        s.feed_eof()

    return web.Request(Message(method, path, headers or {}), s, Protocol, None, None, None)


@asyncio.coroutine
def call(response):
    if asyncio.iscoroutine(response):
        return (yield from response)
    else:
        return response


def with_loop(func):
    @wraps(func)
    def inner():
        asyncio.get_event_loop().run_until_complete(asyncio.coroutine(func)())
    return inner


@with_loop
def test_get_qs():
    response = yield from call(hello_get(make_request('GET', '/?boo=5')))
    assert response.status == 200
    assert response.text == 'Hello, world 5'


@with_loop
def test_rget():
    request = make_request('GET', '/')
    request._match_info = {'boo': '55'}
    response = yield from call(hello_rget(request))
    assert response.status == 200
    assert response.text == 'Hello, world 55'


@with_loop
def test_error_get_qs():
    response = yield from call(hello_get(make_request('GET', '/?boo=foo')))
    assert response.status == 400
    assert json.loads(response.text) == {
        'details': {
            'boo': "invalid literal for int() with base 10: {}".format(repr(b'foo'))
        },
        'error': 'bad-request'
    }


@with_loop
def test_get_form():
    response = yield from call(hello_post(make_request('POST', '/', b'boo=5', FHEADERS)))
    assert response.status == 200
    assert response.text == 'Hello, world 5'


@with_loop
def test_get_multipart_form():
    body, mct = helpers.encode_multipart([('boo', '5')])
    headers = {'Content-Type': mct}
    response = yield from call(hello_post(make_request('POST', '/', body, headers)))
    assert response.status == 200
    assert response.text == 'Hello, world 5'


@with_loop
def test_getpost():
    response = yield from call(hello_getpost(make_request('POST', '/', b'boo=5', FHEADERS)))
    assert response.status == 200
    assert response.text == 'Hello, world 5'

    response = yield from call(hello_getpost(make_request('POST', '/?boo=5', b'foo')))
    assert response.status == 200
    assert response.text == 'Hello, world 5'


@with_loop
def test_error_get_form():
    response = yield from call(hello_post(make_request('POST', '/', b'boo=foo', FHEADERS)))
    assert response.status == 400
    assert json.loads(response.text) == {
        'details': {
            'boo': "invalid literal for int() with base 10: b'foo'"
        },
        'error': 'bad-request'
    }


@with_loop
def test_get_json():
    headers = {'Content-Type': 'application/json'}
    response = yield from call(
        hello_json(make_request('POST', '/', b'{"boo": 5}', headers)))
    assert response.status == 200
    assert response.text == 'Hello, world 5'

    response = yield from call(hello_json(make_request('POST', '/', b'')))
    assert response.text == 'Hello, world 42'


@with_loop
def test_m_query_string():
    v = HelloView(make_request('GET', '/?boo=5'))
    response = yield from call(v.get())
    assert response.status == 200
    assert response.text == 'Hello, world 5'


@with_loop
def test_m_form():
    v = HelloView(make_request('GET', '', b'boo=5', FHEADERS))
    response = yield from call(v.post())
    assert response.status == 200
    assert response.text == 'Hello, world 5'
