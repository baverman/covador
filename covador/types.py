# -*- coding: utf-8 -*-
import re

from .utils import Pipeable
from .compat import utype, btype, stype, ustr, bstr

__all__ = ['Map', 'List', 'Tuple', 'Int', 'Str', 'Bool', 'split', 'Range',
           'irange', 'frange', 'length', 'enum', 'ListMap', 'Bytes', 'regex',
           'email', 'url', 'uuid', 'item', 'opt', 'Invalid']


class item(object):
    def __init__(self, typ=None, source_key=None, required=True,
                 default=None, multi=False, **kwargs):
        self.source_key = source_key
        self.required = required
        self.default = default
        self.multi = multi
        self.__dict__.update(kwargs)
        self.typ = typ and wrap_type(typ)
        self.pipe = []

    def clone(self):
        obj = object.__new__(item)
        obj.__dict__.update(self.__dict__)
        obj.pipe = obj.pipe[:]
        return obj

    def __or__(self, other):
        obj = self.clone()
        obj.pipe.append(other)
        return obj

    def __ror__(self, other):
        obj = self.clone()
        obj.pipe.insert(0, other)
        return obj

    def __call__(self, data):
        if data is None:
            if self.required:
                raise ValueError('Required item')
            else:
                return self.default
        else:
            if self.typ:
                data = self.typ(data)

            if self.pipe:
                for it in self.pipe:
                    data = it(data)

        return data


def opt(*args, **kwargs):
    return item(*args, required=False, **kwargs)


def get_item(it):
    if not isinstance(it, item):
        it = item(it)
    return it


class Invalid(ValueError):
    def __init__(self, errors, clean):
        self.errors = errors
        self.clean = clean
        ValueError.__init__(self, repr(self.errors))


class Map(Pipeable):
    '''Dict checker

    :param items: Dict with fields. Key is a destination key,
                  value is an alias, any callable or covador.schema.item.

    If source dict does not contain a key, key value is considered None.

    item can have source_key param to be able to specify source key, by
    default it equals to field key.
    ::

        Map({'foo': int})({'foo': '10'}) -> {'foo': 10}

        Map({'foo': opt(int)})({}) -> None

        m = Map({'raw': item('bytes', source_key='data'),
                 'decoded': item('str', source_key='data')})
        m({'data': b'data'}) -> {'raw': b'data', 'decoded': u'data'}
    '''
    def __init__(self, items):
        self.items = {}
        for k, it in items.items():
            it = get_item(it)
            if not it.source_key:
                it.source_key = k
            self.items[k] = it

    def get(self, data, item):
        '''Get corresponding data for item

        :param data: source data
        :param item: item to get
        :raise KeyError: if item not found

        Subsclasses can override this method to implement map access to more complex
        structures then plain dict
        '''
        return data[item.source_key]

    def __iter__(self):
        return iter(self.items.items())

    def __call__(self, data):
        errors = []
        result = {}
        get = self.get
        for k, it in self.items.items():
            try:
                raw_data = get(data, it)
            except KeyError:
                raw_data = None

            try:
                result[k] = it(raw_data)
            except Exception as e:
                errors.append((it.source_key, e))

        if errors:
            raise Invalid(errors, result)

        return result


class List(Pipeable):
    '''List checker

    :param item: an alias, any callable or covador.schema.item.

    Checks each source element against provided item.

    ::

        List(int)(['1', '2']) -> [1, 2]

        List(opt(int, default=42))(['1', '2', None]) -> [1, 2, 42]

        List(enum('boo', 'foo'))(['boo', 'bar', 'foo'])
            -> covador.schema.Invalid: [(1, ValueError("'bar' not in ['boo', 'foo']",))]
    '''
    def __init__(self, item):
        self.item = get_item(item)

    def __call__(self, data):
        result = []
        errors = []
        rappend = result.append
        it = self.item
        for idx, raw_data in enumerate(data):
            try:
                rappend(it(raw_data))
            except Exception as e:
                rappend(None)
                errors.append((idx, e))

        if errors:
            raise Invalid(errors, result)

        return result


class Tuple(Pipeable):
    '''Tuple checker

    :param items: a sequence of an alias, any callable or covador.schema.item.

    ::

        t = Tuple((int, List(str.lower)))
        t(('10', 'BOO')) -> [10, ['b', 'o', 'o']]
    '''

    def __init__(self, items):
        self.items = [get_item(r) for r in items]

    def __call__(self, data):
        result = []
        errors = []
        rappend = result.append
        for idx, (it, raw_data) in enumerate(zip(self.items, data)):
            try:
                rappend(it(raw_data))
            except Exception as e:
                rappend(None)
                errors.append((idx, e))

        if errors:
            raise Invalid(errors, result)

        return result


class ListMap(Map):
    '''Checker for dicts with list values

    Can be used as root schema for result of pasrsing query string.
    '''
    def get(self, data, field):
        if field.multi:
            return data[field.source_key]
        else:
            return data[field.source_key][0]


class Int(Pipeable):
    '''Integer checker

    :param base: numeric base to convert from strings, default is 10

    ::

        Int()('10') -> 10

        Int(2)('10') -> 2

        Int(16)('10') -> 16
    '''
    def __init__(self, base=None):
        self.base = base or 10

    def __call__(self, data):
        if type(data) is utype or type(data) is btype:
            return int(data, self.base)
        return int(data)


bool_false_values = {btype: (b'false', b'0', b'', b'no', b'n', b'f')}
bool_false_values[utype] = tuple(map(ustr, bool_false_values[btype]))


class Bool(Pipeable):
    '''Boolean checker

    If source data is string (or bytes) returns ``False`` for
    ``false``, ``0``, ``no``, ``n``, ``f`` and empty values.

    For other types returns coercion to bool.

    ::

        Bool()('NO') -> False

        Bool()([]) -> False

        Bool()(0) -> False

        Bool()('1') -> True

        Bool()([None]) -> True
    '''
    def __call__(self, data):
        dtype = type(data)
        if dtype is btype or dtype is utype:
            return data.lower().strip() not in bool_false_values[dtype]
        return bool(data)


class Str(Pipeable):
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def __call__(self, data):
        if type(data) is utype:
            return data
        elif type(data) is btype:
            if self.encoding:
                return data.decode(self.encoding)
            else:
                return data
        else:
            return stype(data)


class Bytes(Pipeable):
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def __call__(self, data):
        if type(data) is btype:
            return data
        elif type(data) is utype:
            return data.encode(self.encoding)
        else:
            return self(stype(data))


class split(Pipeable):
    def __init__(self, item=None, separator=',', strip=True, empty=False):
        self.separators = {
            utype: ustr(separator),
            btype: bstr(separator)
        }
        self.strip = strip
        self.empty = empty
        self.list = item and List(item)

    def __call__(self, data):
        val = data.split(self.separators[type(data)])
        if self.strip:
            val = [r.strip() for r in val]

        if not self.empty:
            val = list(filter(None, val))

        if self.list:
            val = self.list(val)

        return val


class enum(Pipeable):
    def __init__(self, *choices):
        if len(choices) == 1 and type(choices[0]) in (list, tuple):
            self.choices = set(choices[0])
        else:
            self.choices = set(choices)

        self.choices_str = repr(sorted(self.choices))

    def __call__(self, data):
        if data not in self.choices:
            raise ValueError('{} not in {}'.format(repr(data), self.choices_str))

        return data


class length(Pipeable):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, data):
        size = len(data)
        if self.min is not None and size < self.min:
            raise ValueError('Length of {} is less then {}'.format(size, self.min))
        if self.max is not None and size > self.max:
            raise ValueError('Length of {} is greater then {}'.format(size, self.max))
        return data


class Range(Pipeable):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, data):
        if self.min is not None and data < self.min:
            raise ValueError('{} is less then {}'.format(data, self.min))
        if self.max is not None and data > self.max:
            raise ValueError('{} is greater then {}'.format(data, self.max))
        return data


irange = lambda min=None, max=None, base=None: Int(base=base) | Range(min, max)
frange = lambda min=None, max=None: float | Range(min, max)


class regex(Pipeable):
    def __init__(self, pattern, flags=0):
        self.re = re.compile(pattern, flags)

    def __call__(self, data):
        if not self.re.search(data):
            raise ValueError('Mismatch')
        return data


email = Str() | regex("(?i)^[A-Z0-9._%!#$%&'*+-/=?^_`{|}~()]+@[A-Z0-9]+([.-][A-Z0-9]+)*\.[A-Z]{2,22}$")

URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
url = Str() | regex(URL_REGEX)

uuid = Str() | regex(r"(?i)^(?:urn:uuid:)?\{?[a-f0-9]{8}(?:-?[a-f0-9]{4}){3}-?[a-f0-9]{12}\}?$")


TYPES = {
    dict: lambda it: Map(it),
    list: lambda it: List(it[0]),
    tuple: lambda it: Tuple(it),
}


ALIASES = {
    None: lambda it: it,
    int: Int(),
    'int': Int(),
    str: Str(),
    'str': Str(),
    'bytes': Bytes(),
    bool: Bool(),
    'bool': Bool(),
}


def wrap_type(typ):
    t = TYPES.get(type(typ))
    if t:
        return t(typ)

    return ALIASES.get(typ, typ)
