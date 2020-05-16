from asyncio import get_event_loop, coroutine

from covador.vdecorator import ValidationDecorator
from covador import schema


def test_coro_func():
    getter = lambda it: it
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    @coroutine
    def boo(_, arg):
        return arg

    loop = get_event_loop()
    res = loop.run_until_complete(boo({'arg': 1}))
    assert res == 1


def test_coro_getter():
    getter = coroutine(lambda it: it)
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    def boo(_, arg):
        return arg

    loop = get_event_loop()
    res = loop.run_until_complete(boo({'arg': 1}))
    assert res == 1


def test_coro_func_getter():
    getter = coroutine(lambda it: it)
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    @coroutine
    def boo(_, arg):
        return arg

    loop = get_event_loop()
    res = loop.run_until_complete(boo({'arg': 1}))
    assert res == 1
