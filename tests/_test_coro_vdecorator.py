from asyncio import get_event_loop, coroutine

from covador.vdecorator import ValidationDecorator, mergeof
from covador import schema


def async_run(coro):
    return get_event_loop().run_until_complete(coro)


def test_coro_func():
    getter = lambda it: it
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    @coroutine
    def boo(_, arg):
        return arg

    res = async_run(boo({'arg': 1}))
    assert res == 1


def test_coro_getter():
    getter = coroutine(lambda it: it)
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    def boo(_, arg):
        return arg

    res = async_run(boo({'arg': 1}))
    assert res == 1


def test_coro_func_getter():
    getter = coroutine(lambda it: it)
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    @coroutine
    def boo(_, arg):
        return arg

    res = async_run(boo({'arg': 1}))
    assert res == 1


def test_coro_validator_merge():
    def getter0(it): return it[0]

    @coroutine
    def getter1(it): return it[1]

    v0 = ValidationDecorator(getter0, None, schema)
    v1 = ValidationDecorator(getter1, None, schema)
    v = mergeof(v0, v1)

    @v(arg=int)
    def boo(_, arg):
        return arg

    res = async_run(boo([{}, {'arg': 3}]))
    assert res == 3
