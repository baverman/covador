import sys; sys.path.insert(0, '.')
from aiohttp import web
from asyncio import coroutine

from covador.aiohttp import query_string, json_body, form, params, args


@query_string(boo=str)
@coroutine
def qs_view(request, boo):
    return web.Response(text=boo)


@form(p1=str, p2=int)
@coroutine
def form_view(request, p1, p2):
    return web.Response(text='{0}.{1}'.format(p1, p2))


@params(p1=str, p2=int)
@coroutine
def params_view(request, p1, p2):
    return web.Response(text='{0}.{1}'.format(p1, p2))


@args(boo=str)
@coroutine
def args_view(request, boo):
    return web.Response(text=boo)


@json_body(boo=str)
@coroutine
def json_view(request, boo):
    return web.Response(text=boo)


def main():
    app = web.Application()
    app.router.add_get('/qs/', qs_view)
    app.router.add_post('/form/', form_view)
    app.router.add_post('/params/', params_view)
    app.router.add_get('/args/{boo}/', args_view)
    app.router.add_post('/json/', json_view)

    try:
        web.run_app(app, port=5000)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
