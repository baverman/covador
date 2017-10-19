import pytest

from covador import schema, dpass
from covador.types import *
from covador.vdecorator import ErrorHandler, ErrorContext, ValidationDecorator


def test_error_context():
    def boo():
        try:
            1/0
        except:
            return ErrorContext()

    ctx = boo()
    assert type(ctx.exception) == ZeroDivisionError

    with pytest.raises(ZeroDivisionError):
        ctx.reraise()

    with pytest.raises(KeyError):
        ctx.reraise(KeyError('boo'))


def test_error_handler():
    @ErrorHandler
    def default_error_handler(ctx):
        return ctx + 10

    assert default_error_handler(10) == 20

    @default_error_handler.set
    def error_handler(ctx):
        return ctx + 20

    assert default_error_handler(10) == 30


def test_make_validator():
    schema = lambda: lambda it: {'foo': it + 2}
    getter = lambda it: it + 1
    v = ValidationDecorator(getter, None, schema)

    @v()
    def boo(arg, foo):
        assert arg == 10
        assert foo == 13

    boo(10)


def test_make_validator_with_skip():
    schema = lambda: lambda it: {'foo': it + 2}
    getter = lambda it: it + 1
    v = ValidationDecorator(getter, None, schema, 1)

    @v()
    def boo(request, arg, foo):
        assert request == 'request'
        assert arg == 10
        assert foo == 13

    boo('request', 10)


def test_make_validator_with_empty_error_handler():
    schema = lambda: Int()
    getter = lambda it: it
    v = ValidationDecorator(getter, None, schema)

    @v()
    def boo(arg, foo):
        assert arg == 10
        assert foo == 13

    with pytest.raises(ValueError):
        boo('boo')


def test_make_validator_with_error_handler():
    def on_error(e):
        assert str(e.exc_info[1]) == "invalid literal for int() with base 10: 'boo'"
        return 'foo'

    schema = lambda: Int()
    getter = lambda it: it
    v = ValidationDecorator(getter, None, schema).on_error(on_error)

    @v()
    def boo(arg, foo):
        assert arg == 10
        assert foo == 13

    assert boo('boo') == 'foo'


def test_validator_with_pipe():
    getter = lambda it: it
    params = ValidationDecorator(getter, None, schema)

    @dpass(params(arg=int) | (lambda r: {'arg': r['arg'] + 10}))
    def boo(request, arg):
        boo.called = True
        assert arg == 11

    boo({'arg': 1})
    assert boo.called
