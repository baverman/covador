# -*- coding: utf-8 -*-
from covador import schema
from covador.types import List, Map
from covador.compat import urlencode, ustr, bstr
from covador.utils import parse_qs, wrap_in, merge_dicts, Pipe, pipe


def test_parse_qs():
    assert parse_qs(b'') == {}
    assert parse_qs(bstr('boo', 'utf-8')) == {'boo': [b'']}
    assert parse_qs(bstr('boo=1&boo=2', 'utf-8')) == {'boo': [b'1', b'2']}

    data = urlencode({'boo': u'буу'.encode('utf-8')})
    assert parse_qs(ustr(data)) == {'boo': [u'буу'.encode('utf-8')]}
    assert parse_qs(bstr(data)) == {'boo': [u'буу'.encode('utf-8')]}

    data = urlencode({'boo': u'буу'.encode('cp1251')})
    assert parse_qs(ustr(data)) == {'boo': [u'буу'.encode('cp1251')]}
    assert parse_qs(bstr(data)) == {'boo': [u'буу'.encode('cp1251')]}


def test_wrap_in():
    s = List(int) | wrap_in('data')
    result = s([1, 2, 3])
    assert result == {'data': [1, 2, 3]}


def test_merge_dicts():
    result = merge_dicts({'k1': 1, 'k2': 2, 'k3': 3},
                         {'k2': 22, 'k3': 33},
                         k3=333)

    assert result == {'k1': 1, 'k2': 22, 'k3': 333}


def test_pipe():
    assert (Pipe([str, str.strip]) | str.lower)(' AA ') == 'aa'
    assert (str | Pipe([str.strip, str.lower]))(' AA ') == 'aa'
    assert pipe(Pipe([str, int]), float).pipe == [str, int, float]
    assert pipe(float, Pipe([str, int])).pipe == [float, str, int]
    assert pipe(str, int).pipe == [str, int]


def test_smart_schema():
    s = schema(foo=int)
    assert s({'foo': 10}) == {'foo': 10}

    s = schema({'foo': int})
    assert s({'foo': 10}) == {'foo': 10}

    s = schema({'foo': int}, {'foo': str})
    assert s({'foo': 10}) == {'foo': '10'}

    s = schema(schema(foo=int), schema(foo=str), boo=int)
    assert type(s) == Map
    assert s({'foo': 10, 'boo': '20'}) == {'foo': '10', 'boo': 20}

    s = schema(foo=str, _=lambda r: r['foo'].upper())
    assert s({'foo': 'aaa'}) == u'AAA'
