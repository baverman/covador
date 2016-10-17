import asyncio

from covador.aiohttp import query_string, form


def test_get_qs():
    class Request(dict):
        pass

    request = Request()
    request.query_string = 'boo=10'

    @query_string(boo=int)
    @asyncio.coroutine
    def handler(request, boo):
        assert boo == 10
        request.called = True

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(handler(request), 1))
    assert request.called


def test_get_form():
    class Request(dict):
        @asyncio.coroutine
        def read(self):
            return b'boo=10'

    request = Request()

    @form(boo=int)
    @asyncio.coroutine
    def handler(request, boo):
        assert boo == 10
        request.called = True

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(handler(request), 1))
    assert request.called
