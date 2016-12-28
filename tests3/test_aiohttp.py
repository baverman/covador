import pytest

import asyncio

from aiohttp import web
from covador.aiohttp import form
from covador.aiohttp import m_form
from covador.aiohttp import query_string
from covador.aiohttp import m_query_string


@pytest.fixture
def cli(loop, test_client):
    @form(boo=int)
    @asyncio.coroutine
    def hello_post(request, boo):
        return web.Response(text='Hello, world {}'.format(boo))

    @query_string(boo=int)
    @asyncio.coroutine
    def hello_get(request, boo):
        return web.Response(text='Hello, world {}'.format(boo))

    class HelloView(web.View):

        @m_query_string(boo=int)
        @asyncio.coroutine
        def get(self, boo):
            return web.Response(text='Hello, world {}'.format(boo))

        @m_form(boo=int)
        @asyncio.coroutine
        def post(self, boo):
            return web.Response(text='Hello, world {}'.format(boo))

    app = web.Application(loop=loop)
    app.router.add_get('/', hello_get)
    app.router.add_post('/', hello_post)
    app.router.add_route('*', '/cbv/', HelloView)
    return loop.run_until_complete(test_client(app))


@asyncio.coroutine
def test_get_qs(cli):
    response = yield from cli.get('/', params={'boo': 5})
    assert response.status == 200
    assert (yield from response.text()) == 'Hello, world 5'


@asyncio.coroutine
def test_get_form(cli):
    response = yield from cli.post('/', data={'boo': 5})
    assert response.status == 200
    assert (yield from response.text()) == 'Hello, world 5'


@asyncio.coroutine
def test_m_query_string(cli):
    response = yield from cli.get('/cbv/', params={'boo': 5})
    assert response.status == 200
    assert (yield from response.text()) == 'Hello, world 5'


@asyncio.coroutine
def test_m_form(cli):
    response = yield from cli.post('/cbv/', data={'boo': 5})
    assert response.status == 200
    assert (yield from response.text()) == 'Hello, world 5'
