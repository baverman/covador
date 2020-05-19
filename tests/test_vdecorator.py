import pytest

from covador import list_schema, schema, dpass, soft_map, typed_map, compat
from covador.types import Int, SoftListMap
from covador.utils import wrap_in
from covador.errors import BadField
from covador.vdecorator import (ErrorHandler, ErrorContext,
                                ValidationDecorator, mergeof)


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
    schema = lambda it: {'foo': it + 2}
    top_schema = lambda: schema
    getter = lambda it: it + 1
    v = ValidationDecorator(getter, None, top_schema)

    @v()
    def boo(arg, foo):
        return arg, foo

    assert boo(10) == (10, 13)
    assert boo.schema is schema


def test_make_validator_with_skip():
    schema = lambda: lambda it: {'foo': it + 2}
    getter = lambda it: it + 1
    v = ValidationDecorator(getter, None, schema, 1)

    @v()
    def boo(request, arg, foo):
        return request, arg, foo

    assert boo('request', 10) == ('request', 10, 13)


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
        return arg

    assert boo({'arg': 1}) == 11


def test_validator_with_piped_schema():
    getter = lambda it: it

    v = ValidationDecorator(getter, None, schema)
    @v(soft_map(arg=int) | wrap_in('data'))
    def boo(request, data):
        return data
    assert boo({'arg': 1, 'foo': 'boo'}) == {'arg': 1, 'foo':'boo'}

    v = ValidationDecorator(getter, None, list_schema)
    @v(soft_map(arg=int) | wrap_in('data'))
    def boo(request, data):
        return data
    assert boo({'arg': [1], 'foo': ['boo']}) == {'arg': 1, 'foo':'boo'}


def test_validator_merge():
    getter0 = lambda it: it[0]
    getter1 = lambda it: it[1]

    v0 = ValidationDecorator(getter0, None, schema)
    v1 = ValidationDecorator(getter1, None, schema)
    v = mergeof(v0, v1)

    @v(arg=int)
    def boo(_, arg):
        return arg

    assert boo([{}, {'arg': 3}]) == 3


def test_validator_soft_map_merge():
    getter0 = lambda it: it[0]
    getter1 = lambda it: it[1]

    v0 = ValidationDecorator(getter0, None, schema)
    v1 = ValidationDecorator(getter1, None, schema)
    v = mergeof(v0, v1)

    @v(soft_map(), arg=int)
    def boo(_, arg, boo):
        return arg, boo

    assert boo([{'boo': 'foo'}, {'arg': 3}]) == (3, 'foo')


def test_ensure_item_getter():
    getter = lambda ctx: ctx
    v = ValidationDecorator(getter, None, list_schema)

    @v(schema(arg=int))
    def boo(_, arg):
        return arg

    assert boo({'arg': ["1"]}) == 1


def test_soft_map():
    getter = lambda ctx: ctx
    v = ValidationDecorator(getter, None, schema)

    @v(soft_map(arg=int))
    def boo(_, arg, **data):
        return arg, data

    assert boo({'arg': '10', 'foo': 'bar'}) == (10, {'foo': 'bar'})


def test_soft_list_map():
    getter = lambda ctx: ctx
    v = ValidationDecorator(getter, None, list_schema)

    @v(SoftListMap(dict(arg=int)))
    def boo(_, arg, **data):
        return arg, data

    assert boo({'arg': ['10'], 'foo': ['bar']}) == (10, {'foo': ['bar']})


def test_typed_map():
    getter = lambda ctx: ctx
    v = ValidationDecorator(getter, None, schema)

    @v(typed_map(str, int))
    def boo(_, arg, foo):
        return arg, foo

    assert boo({'arg': '10', 'foo': 20}) == (10, 20)

    @v(typed_map(str, int) | wrap_in('data'))
    def boo(_, data):
        return data

    assert boo({'arg': '10', 'foo': 20}) == {'arg': 10, 'foo': 20}


def test_bad_field():
    getter = lambda it: it
    v = ValidationDecorator(getter, None, schema)

    @v(arg=int)
    def boo(request, arg):
        raise BadField('name', 'msg')

    with pytest.raises(BadField):
        boo({'arg': 1})


def test_bad_field_with_error_handler():
    getter = lambda it: it

    def on_error(e):
        assert str(e.exc_info[1]) == str({'name': 'msg'})
        return 'foo'

    v = ValidationDecorator(getter, None, schema).on_error(on_error)

    @v(arg=int)
    def boo(request, arg):
        raise BadField('name', 'msg')

    assert boo({'arg': 1}) == 'foo'


if compat.ASYNC_AWAIT:
    from tests._test_async_vdecorator import *
elif compat.COROUTINE:
    from tests._test_coro_vdecorator import *
