import sys; sys.path.insert(0, '.')
from aiohttp import web

from covador.aiohttp import query_string, json_body, form, params, rparams


class QS(web.View):
    @query_string(boo=str)
    async def get(self, boo):
        return web.Response(text=boo)


class Form(web.View):
    @form(p1=str, p2=int)
    async def post(self, p1, p2):
        return web.Response(text='{0}.{1}'.format(p1, p2))


class Params(web.View):
    @params(p1=str, p2=int)
    async def post(self, p1, p2):
        return web.Response(text='{0}.{1}'.format(p1, p2))


class RParams(web.View):
    @rparams(boo=str)
    async def get(self, boo):
        return web.Response(text=boo)


class JSON(web.View):
    @json_body(boo=str)
    async def post(self, boo):
        return web.Response(text=boo)


def main():
    app = web.Application()
    app.router.add_get('/qs/', QS)
    app.router.add_post('/form/', Form)
    app.router.add_post('/params/', Params)
    app.router.add_get('/rparams/{boo}/', RParams)
    app.router.add_post('/json/', JSON)

    try:
        web.run_app(app, port=5000)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
