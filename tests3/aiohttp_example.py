import sys
sys.path.insert(0, '.')

from aiohttp import web
from covador.aiohttp import query_string, form

@form(boo=int)
async def hello(request, boo):
    return web.Response(text='Hello, world {}'.format(boo))

app = web.Application()
app.router.add_get('/', hello)
app.router.add_post('/', hello)

web.run_app(app)
