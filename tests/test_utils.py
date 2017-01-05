import pytest

from covador import schema
from covador.types import List, Int
from covador.utils import (parse_qs, wrap_in, merge_dicts, ValidationDecorator,
                           Pipe, pipe, ErrorContext)


def test_parse_qs():
    assert parse_qs('boo=foo') == {'boo': ['foo']}
    assert parse_qs(b'boo=foo') == {'boo': [b'foo']}


def test_wrap_in():
    s = List(int) | wrap_in('data')
    result = s([1, 2, 3])
    assert result == {'data': [1, 2, 3]}


def test_merge_dicts():
    result = merge_dicts({'k1': 1, 'k2': 2, 'k3': 3},
                         {'k2': 22, 'k3': 33},
                         k3=333)

    assert result == {'k1': 1, 'k2': 22, 'k3': 333}


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
    v = params(arg=int) | (lambda r: {'arg': r['arg'] + 10})

    @v
    def boo(request, arg):
        boo.called = True
        assert arg == 11

    boo({'arg': 1})
    assert boo.called


def test_pipe():
    assert (Pipe([str, str.strip]) | str.lower)(' AA ') == 'aa'
    assert (str | Pipe([str.strip, str.lower]))(' AA ') == 'aa'
    assert pipe(Pipe([str, int]), float).pipe == [str, int, float]
    assert pipe(float, Pipe([str, int])).pipe == [float, str, int]
    assert pipe(str, int).pipe == [str, int]


def test_smart_schema():
    s = schema({'foo': int}, {'foo': str})
    assert s({'foo': 10}) == {'foo': '10'}

    s = schema(schema(foo=int), schema(foo=str), boo=int)
    assert s({'foo': 10, 'boo': '20'}) == {'foo': '10', 'boo': 20}


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
