import inspect
from asyncio import get_event_loop

from covador.vdecorator import ValidationDecorator
from covador import schema


def test_async_func():
    getter = lambda it: it
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    async def boo(_, arg):
        return arg

    loop = get_event_loop()
    res = loop.run_until_complete(boo({'arg': 1}))
    assert res == 1


def test_async_getter():
    async def getter(it): return it
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    def boo(_, arg):
        return arg

    loop = get_event_loop()
    res = loop.run_until_complete(boo({'arg': 1}))
    assert res == 1


def test_async_func_getter():
    async def getter(it): return it
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    async def boo(_, arg):
        return arg

    loop = get_event_loop()
    res = loop.run_until_complete(boo({'arg': 1}))
    assert res == 1
