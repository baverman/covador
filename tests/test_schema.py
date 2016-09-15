import pytest

from covador import schema
from covador.schema import Pipe, opt, item, Invalid


def test_existing_field():
    s = schema(foo=int)
    result = s({'foo': '10'})
    assert result == {'foo': 10}


def test_required_field():
    s = schema(foo=int, boo=int)
    with pytest.raises(Invalid) as ei:
        s({'boo': 20})

    e = ei.value
    assert e.clean == {'boo': 20}
    assert e.errors[0][0] == 'foo'

    with pytest.raises(Invalid) as ei:
        s({'foo': None, 'boo': 20})

    e = ei.value
    assert e.clean == {'boo': 20}
    assert e.errors[0][0] == 'foo'


def test_opt_field():
    s = schema(foo=opt(int), boo=opt(int, default=10))
    result = s({})
    assert result == {'foo': None, 'boo': 10}


def test_source_key():
    s = schema(foo=item(int, 'boo'))
    result = s({'boo': '10'})
    assert result == {'foo': 10}


def test_literal_schema():
    s = schema(foo={'boo': [(int, int)]})
    assert s({'foo': {'boo': [('1', '2'), ('3', '4')]}}) == {'foo': {'boo': [[1, 2], [3, 4]]}}


def test_pipe():
    assert (Pipe([str, str.strip]) | str.lower)(' AA ') == 'aa'
    assert (str | Pipe([str.strip, str.lower]))(' AA ') == 'aa'


def test_item_pipe():
    s = item() | int
    assert s('10') == 10

    s = opt(default='20') | int
    assert s(None) == '20'

    with pytest.raises(ValueError):
        item()(None)

    assert (int | item())('10') == 10


def test_smart_schema():
    s = schema({'foo': int}, {'foo': str})
    assert s({'foo': 10}) == {'foo': '10'}

    s = schema(schema(foo=int), schema(foo=str), boo=int)
    assert s({'foo': 10, 'boo': '20'}) == {'foo': '10', 'boo': 20}
