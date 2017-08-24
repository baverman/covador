# -*- coding: utf-8 -*-
import time
import datetime as dt
import pytest

from covador import schema
from covador.types import *
from covador.errors import error_to_dict
from covador.compat import utype, PY2


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
    s = schema(foo=opt(int), boo=opt(int, 10))
    result = s({})
    assert result == {'foo': None, 'boo': 10}

    assert (opt(str, 'aaa') | utype.upper)(None) == 'aaa'


def test_src():
    s = schema(foo=item(int, src='boo'))
    result = s({'boo': '10'})
    assert result == {'foo': 10}


def test_dest():
    s = schema(boo=item(int, dest='foo'))
    result = s({'boo': '10'})
    assert result == {'foo': 10}


def test_literal_schema():
    s = schema(foo={'boo': [(int, int)]})
    assert s({'foo': {'boo': [('1', '2'), ('3', '4')]}}) == {'foo': {'boo': [[1, 2], [3, 4]]}}


def test_item_pipe():
    s = item() | int
    assert s('10') == 10

    s = opt(default='20') | int
    assert s(None) == '20'

    with pytest.raises(RequiredExcepion):
        item()(None)

    assert (int | item())('10') == 10


def test_item_empty():
    with pytest.raises(RequiredExcepion):
        item(empty_is_none=True)('')


def test_opt_empty():
    s = opt(int, 10)
    assert s('') == 10

    s = nopt(int)
    with pytest.raises(ValueError):
        s('')

    assert repr(opt()('')) == 'None'
    assert repr(opt()(b'')) == 'None'


def test_int():
    assert Int()(10) == 10
    assert Int()(u'10') == 10
    assert Int()(b'10') == 10
    assert Int(16)(u'10') == 16
    assert Int(2)(b'10') == 2


def test_str():
    assert repr(Str()(u'aaa')) == repr(u'aaa')
    assert repr(Str()(b'aaa')) == repr(u'aaa')
    assert repr(Str(encoding=False)(b'aaa')) == repr(b'aaa')
    assert repr(Str()(10)) == repr('10')


def test_bytes():
    assert repr(Bytes()(u'aaa')) == repr(b'aaa')
    assert repr(Bytes()(b'aaa')) == repr(b'aaa')
    assert repr(Bytes()(10)) == repr(b'10')


def test_split():
    assert split()('aa, bb') == ['aa', 'bb']
    assert split(strip=False)('aa, bb') == ['aa', ' bb']
    assert split(int)('1, 3, 5') == [1, 3, 5]
    assert split(int)('1, 3, 5,,') == [1, 3, 5]
    assert split(int, separator=None)('1\t2') == [1, 2]

    assert repr(split(separator=b',')(b'boo')) == repr([b'boo'])
    assert repr(split(separator=u',')(b'boo')) == repr([b'boo'])
    assert repr(split(separator=b',')(u'boo')) == repr([u'boo'])
    assert repr(split(separator=u',')(u'boo')) == repr([u'boo'])


def test_enum():
    assert enum(1, 2)(1) == 1

    with pytest.raises(EnumException) as ei:
        enum(1, 2)(3)
    assert str(ei.value) == '3 not in [1, 2]'

    assert enum(['boo', 'foo'])('boo') == 'boo'

    with pytest.raises(EnumException) as ei:
        enum(['boo', 'foo'])('bar')
    assert str(ei.value) == "'bar' not in ['boo', 'foo']"


def test_split_enum():
    with pytest.raises(Invalid) as ei:
        split(enum('boo', 'foo'))('boo, bar, foo')

    e = ei.value
    assert e.clean == ['boo', None, 'foo']
    assert len(e.errors) == 1
    assert e.errors[0][0] == 1
    assert str(e.errors[0][1]) == "'bar' not in ['boo', 'foo']"


def test_int_range():
    r = irange(0, 10)
    assert r('5') == 5
    assert r(0) == 0
    assert r(10) == 10

    with pytest.raises(RangeException) as ei:
        assert r(-1)
    assert str(ei.value) == '-1 is less then 0'

    with pytest.raises(RangeException) as ei:
        assert r(11)
    assert str(ei.value) == '11 is greater then 10'


def test_float_range():
    r = frange(0, 10)
    assert r('5') == 5
    assert r(0) == 0
    assert r(10) == 10

    with pytest.raises(RangeException) as e:
        assert r(-1)

    assert str(e.value) == '-1.0 is less then 0'


def test_length():
    l = length(1, 3)
    assert l('12') == '12'
    assert l([1]) == [1]
    assert l((1, 2, 3)) == (1, 2, 3)

    with pytest.raises(LengthException) as ei:
        assert l('')
    assert str(ei.value) == 'Length of 0 is less then 1'

    with pytest.raises(LengthException) as ei:
        assert l('1234')
    assert str(ei.value) == 'Length of 4 is greater then 3'

    l = length(4)
    assert l('1234') == '1234'

    with pytest.raises(LengthException) as ei:
        assert l('2')
    assert str(ei.value) == 'Length of 1 is less then 4'

    with pytest.raises(LengthException) as ei:
        assert l('24567')
    assert str(ei.value) == 'Length of 5 is greater then 4'


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

    with pytest.raises(Invalid) as ei:
        s(['boo', 2])

    e = ei.value
    assert e.clean == [None, '2']
    assert e.errors[0][0] == 0


def test_bool():
    b = Bool()
    assert not b(False)
    assert not b(None)
    assert not b(0)
    assert b(True)
    assert b(1)

    assert not b(b'no')
    assert not b(b'No')
    assert not b(b'false')
    assert not b(b'0')
    assert not b(b'')
    assert not b(b'n')
    assert not b(b'f')
    assert b(b'sdf')

    assert not b(u'no')
    assert not b(u'No')
    assert not b(u'false')
    assert not b(u'0')
    assert not b(u'')
    assert not b(u'n')
    assert not b(u'f')
    assert b(u'sdf')


def test_regex():
    assert regex('boo')('boo') == 'boo'
    assert regex('boo')('fooboofoo') == 'fooboofoo'

    with pytest.raises(RegexException) as ei:
        assert regex('^boo$')('fooboofoo')

    assert str(ei.value) == 'Mismatch "fooboofoo" for "^boo$"'


def test_oneof_schema():
    s = schema(oneof(dict(foo=item(str, src='fooo'), baz=str),
                     dict(boo=str, baz=str)),
               bar=opt(str))

    assert s({'fooo': 'foo', 'baz': 'baz'}) == {'bar': None, 'boo': None, 'baz': u'baz', 'foo': u'foo'}
    s({'boo': 'boo', 'baz': 'baz'}) == {'bar': None, 'boo': u'boo', 'baz': u'baz', 'foo': None}

    with pytest.raises(Invalid) as ei:
        s({})
    err = error_to_dict(ei.value)
    assert err == {'one of': {0: {'fooo': 'Required item', 'baz': 'Required item'},
                              1: {'baz': 'Required item', 'boo': 'Required item'}}}

    with pytest.raises(Invalid) as ei:
        s({'baz': 'baz'})
    err = error_to_dict(ei.value)
    assert err == {'one of': {0: {'fooo': 'Required item'},
                              1: {'boo': 'Required item'}}}


def test_oneof():
    s = oneof(Int(), Str())
    assert s(10) == 10
    assert s('boo') == u'boo'


def test_datetime():
    assert DateTime()('2016-02-05 12:45:03') == dt.datetime(2016, 2, 5, 12, 45, 3)
    assert Date()('2016-02-05') == dt.date(2016, 2, 5)
    assert Time()('12:45:03') == dt.time(12, 45, 3)

    with pytest.raises(ValueError) as ei:
        Time()('boo')
    assert str(ei.value) == "time data 'boo' does not match format '%H:%M:%S'"


def test_timestamp():
    assert timestamp('1498028477') == dt.datetime(2017, 6, 21, 7, 1, 17)
    assert timestamp_msec('1498028477000') == dt.datetime(2017, 6, 21, 7, 1, 17)

    ts = time.mktime(dt.datetime(2017, 6, 21, 7, 1, 17).timetuple())
    assert Timestamp(utc=False)(ts) == dt.datetime(2017, 6, 21, 7, 1, 17)


def test_numbers():
    assert numbers('123') == '123'
    assert numbers(u'123') == u'123'
    assert numbers(b'123') == b'123'

    assert numbers('+7 (980) 678-12-13') == '79806781213'


def test_keyval():
    s = KeyVal(int, int)
    assert s({'10': '20'}) == {10: 20}

    with pytest.raises(Invalid) as ei:
        s({'boo': '10'})

    err = error_to_dict(ei.value)
    assert err == {'boo:key': "invalid literal for int() with base 10: 'boo'"}

    with pytest.raises(Invalid) as ei:
        s({u'бу': '10'})

    err = error_to_dict(ei.value)
    if PY2:
        assert err == {u'бу:key': "invalid literal for int() with base 10: '\\xd0\\xb1\\xd1\\x83'"}
    else:
        assert err == {u'бу:key': "invalid literal for int() with base 10: 'бу'"}

    with pytest.raises(Invalid) as ei:
        s({b'20': 'boo'})

    err = error_to_dict(ei.value)
    assert err == {b'20:val': "invalid literal for int() with base 10: 'boo'"}
