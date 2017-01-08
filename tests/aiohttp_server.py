import sys; sys.path.insert(0, '.')
import json
from aiohttp import web

from covador import schema, item
from covador.aiohttp import query_string, json_body


@query_string(foo=item(json.loads) | schema(boo=int), bar=item([int], multi=True))
async def test_qs(request, foo, bar):
    return web.Response(text='foo is {}, bar is {}'.format(foo, bar))


@json_body(foo=int, bar=[int])
async def test_json(request, foo, bar):
    return web.Response(text='foo is {}, bar is {}'.format(foo, bar))


app = web.Application()
app.router.add_get('/qs/', test_qs)
app.router.add_post('/json/', test_json)

web.run_app(app, port=5000)
