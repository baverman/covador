import pytest

from covador import item, Invalid
from covador.types import *


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

    with pytest.raises(ValueError) as ei:
        enum(1, 2)(3)
    assert str(ei.value) == '3 not in [1, 2]'

    assert enum(['boo', 'foo'])('boo') == 'boo'

    with pytest.raises(ValueError) as ei:
        enum(['boo', 'foo'])('bar')
    assert str(ei.value) == "'bar' not in ['boo', 'foo']"


def test_split_enum():
    with pytest.raises(ValueError) as ei:
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

    with pytest.raises(ValueError) as ei:
        assert r(-1)
    assert str(ei.value) == '-1 is less then 0'

    with pytest.raises(ValueError) as ei:
        assert r(11)
    assert str(ei.value) == '11 is greater then 10'


def test_float_range():
    r = frange(0, 10)
    assert r('5') == 5
    assert r(0) == 0
    assert r(10) == 10

    with pytest.raises(ValueError) as e:
        assert r(-1)

    assert str(e.value) == '-1.0 is less then 0'


def test_length():
    l = length(1, 3)
    assert l('12') == '12'
    assert l([1]) == [1]
    assert l((1, 2, 3)) == (1, 2, 3)

    with pytest.raises(ValueError) as ei:
        assert l('')
    assert str(ei.value) == 'Length of 0 is less then 1'

    with pytest.raises(ValueError) as ei:
        assert l('1234')
    assert str(ei.value) == 'Length of 4 is greater then 3'


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

    with pytest.raises(ValueError):
        assert regex('^boo$')('fooboofoo')
