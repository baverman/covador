import pytest

from covador.types import List, Int
from covador.utils import parse_qs, wrap_in, merge_dicts, make_validator


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
    v = make_validator(getter, None, schema)

    @v()
    def boo(arg, foo):
        assert arg == 10
        assert foo == 13

    boo(10)


def test_make_validator_with_skip():
    schema = lambda: lambda it: {'foo': it + 2}
    getter = lambda it: it + 1
    v = make_validator(getter, None, schema, 1)

    @v()
    def boo(request, arg, foo):
        assert request == 'request'
        assert arg == 10
        assert foo == 13

    boo('request', 10)


def test_make_validator_with_empty_error_handler():
    schema = lambda: Int()
    getter = lambda it: it
    v = make_validator(getter, None, schema)

    @v()
    def boo(arg, foo):
        assert arg == 10
        assert foo == 13

    with pytest.raises(ValueError):
        boo('boo')


def test_make_validator_with_error_handler():
    def on_error(e):
        assert str(e) == "invalid literal for int() with base 10: 'boo'"
        return 'foo'

    schema = lambda: Int()
    getter = lambda it: it
    v = make_validator(getter, on_error, schema)

    @v()
    def boo(arg, foo):
        assert arg == 10
        assert foo == 13

    assert boo('boo') == 'foo'
