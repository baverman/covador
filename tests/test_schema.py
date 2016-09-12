import pytest

from covador import opt, item, Invalid, List, Tuple, schema, wrap_in, ListMap


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


def test_multi_map():
    s = ListMap({'foo': int, 'boo': item(multi=True)})
    result = s({'foo': ['10'], 'boo': [1, 2]})
    assert result == {'foo': 10, 'boo': [1, 2]}


def test_list():
    s = List(int)
    result = s(['1', '2', '3'])
    assert result == [1, 2, 3]


def test_tuple():
    s = Tuple((int, str))
    result = s(['1', 2])
    assert result == [1, '2']


def test_wrap_in():
    s = List(int) | wrap_in('data')
    result = s([1, 2, 3])
    assert result == {'data': [1, 2, 3]}


def test_item_pipe():
    s = item() | int
    assert s('10') == 10

    s = opt(default='20') | int
    assert s(None) == '20'

    with pytest.raises(ValueError):
        item()(None)
