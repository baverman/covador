import pytest

from aiohttp import web
from covador.aiohttp import form
from covador.aiohttp import m_form
from covador.aiohttp import query_string
from covador.aiohttp import m_query_string


@pytest.fixture
def cli(loop, test_client):
    @form(boo=int)
    async def hello_post(request, boo):
        return web.Response(text='Hello, world {}'.format(boo))

    @query_string(boo=int)
    async def hello_get(request, boo):
        return web.Response(text='Hello, world {}'.format(boo))

    class HelloView(web.View):

        @m_query_string(boo=int)
        async def get(self, boo):
            return web.Response(text='Hello, world {}'.format(boo))

        @m_form(boo=int)
        async def post(self, boo):
            return web.Response(text='Hello, world {}'.format(boo))

    app = web.Application(loop=loop)
    app.router.add_get('/', hello_get)
    app.router.add_post('/', hello_post)
    app.router.add_route('*', '/cbv/', HelloView)
    return loop.run_until_complete(test_client(app))


async def test_get_qs(cli):
    response = await cli.get('/', params={'boo': 5})
    assert response.status == 200
    assert await response.text() == 'Hello, world 5'


async def test_get_form(cli):
    response = await cli.post('/', data={'boo': 5})
    assert response.status == 200
    assert await response.text() == 'Hello, world 5'


async def test_m_query_string(cli):
    response = await cli.get('/cbv/', params={'boo': 5})
    assert response.status == 200
    assert await response.text() == 'Hello, world 5'


async def test_m_form(cli):
    response = await cli.post('/cbv/', data={'boo': 5})
    assert response.status == 200
    assert await response.text() == 'Hello, world 5'
