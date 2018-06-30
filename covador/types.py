# -*- coding: utf-8 -*-
import re
from datetime import datetime

from .utils import Pipeable, clone, ensure_context, merge_dicts
from .compat import utype, btype, stype, ustr, str_map, str_coerce, bstr, PY2
from .errors import (Invalid, RequiredExcepion, RangeException, RegexException,
                     LengthException, EnumException)

__all__ = ['Map', 'List', 'Tuple', 'Int', 'Str', 'Bool', 'split', 'Range',
           'irange', 'frange', 'length', 'enum', 'ListMap', 'Bytes', 'regex',
           'email', 'url', 'uuid', 'item', 'nitem', 'opt', 'nopt', 'Invalid', 'RequiredExcepion',
           'RangeException', 'RegexException', 'LengthException', 'EnumException',
           'oneof', 'make_schema', 'DateTime', 'Date', 'Time', 'Timestamp',
           'timestamp', 'timestamp_msec', 'numbers', 'KeyVal', 'check']

UNDEFINED = object()
EMPTY_VALUES = b'', u''


class item(object):
    def __init__(self, typ=None, default=None, source_key=None, src=None, dest=None,
                 required=True, multi=False, empty_is_none=True,  **kwargs):
        self.src = source_key or src
        self.dest = dest
        self.required = required
        self.default = default
        self.multi = multi
        self.empty_is_none = empty_is_none
        self.__dict__.update(kwargs)
        self.typ = typ and wrap_type(typ)
        if multi and self.typ:
            self.typ = List(self.typ)
        self.pipe = []

    def clone(self):
        return clone(self, pipe=self.pipe[:])

    def __or__(self, other):
        obj = self.clone()
        obj.pipe.append(ensure_context(self.typ, other))
        return obj

    def __ror__(self, other):
        obj = self.clone()
        obj.pipe.insert(0, ensure_context(self.typ, other, False))
        return obj

    def __call__(self, data):
        if self.empty_is_none and data in EMPTY_VALUES:
            data = None
        if data is None:
            if self.required:
                raise RequiredExcepion()
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


def nopt(*args, **kwargs):
    return item(*args, empty_is_none=False, required=False, **kwargs)


def nitem(*args, **kwargs):
    return item(*args, empty_is_none=False, **kwargs)


def get_item(it):
    if isinstance(it, item):
        it = clone(it)
    else:
        it = item(it)
    return it


class Map(Pipeable):
    '''Dict checker

    :param items: Dict with fields. Key is a destination key,
                  value is an alias, any callable or covador.schema.item.

    If source dict does not contain a key, key value is considered None.

    item can have src or dest param to be able to specify source or
    destination key, by default it equals to field key.
    ::

        Map({'foo': int})({'foo': '10'}) -> {'foo': 10}

        Map({'foo': opt(int)})({}) -> None

        m = Map({'raw': item('bytes', src='data'),
                 'data': item('str', dest='decoded')})
        m({'data': b'data'}) -> {'raw': b'data', 'decoded': u'data'}
    '''
    def __init__(self, items):
        if isinstance(items, Map):
            items = items.items

        self.items = {}
        for k, it in items.items():
            it = get_item(it)
            if not it.src:
                it.src = k
            if not it.dest:
                it.dest = k
            self.items[it.dest] = it

    def get(self, data, item):
        '''Get corresponding data for item

        :param data: source data
        :param item: item to get

        Subsclasses can override this method to implement map access to more complex
        structures then plain dict
        '''
        return data.get(item.src)

    def __call__(self, data):
        errors = []
        result = {}
        get = self.get

        for k, it in self.items.items():
            raw_data = get(data, it)
            try:
                result[k] = it(raw_data)
            except Exception as e:
                errors.append((it.src, e))

        if errors:
            raise Invalid(errors, result)

        return result


class List(Pipeable):
    '''List checker

    :param item: an alias, any callable or covador.schema.item.

    Checks each source element against provided item.

    ::

        List(int)(['1', '2']) -> [1, 2]

        List(opt(int, 42))(['1', '2', None]) -> [1, 2, 42]

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
            return data.get(field.src)
        else:
            d = data.get(field.src)
            if d:
                return d[0]
            else:
                return None


class KeyVal(Pipeable):
    '''Checker of typed mappings

    For example KeyVal(int, [int]) can validate dicts
    with integers as keys and list of integers as values.
    '''
    def __init__(self, key=None, value=None):
        self.key = get_item(key)
        self.value = get_item(value)

    def __call__(self, data):
        errors = []
        result = {}

        for key, value in data.items():
            if self.value:
                try:
                    value = self.value(value)
                except Exception as e:
                    errors.append((key + str_coerce(key, ':val'), e))
                    continue

            if self.key:
                try:
                    key = self.key(key)
                except Exception as e:
                    errors.append((key + str_coerce(key, ':key'), e))
                    continue

            result[key] = value

        if errors:
            raise Invalid(errors, result)

        return result


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
            if PY2:
                data = bstr(data, 'utf-8')  # pragma: no cover py3
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
        self.separators = str_map(separator)
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
            raise EnumException(data, self.choices_str)

        return data


class length(Pipeable):
    def __init__(self, min=None, max=UNDEFINED):
        self.min = min
        self.max = min if max is UNDEFINED else max
        assert self.min is not None or self.max is not None

    def __call__(self, data):
        size = len(data)
        if self.min is not None and size < self.min:
            raise LengthException(data, min=self.min)
        if self.max is not None and size > self.max:
            raise LengthException(data, max=self.max)
        return data


class check(Pipeable):
    def __init__(self, checker, message=None):
        self.checker = checker
        self.message = message or 'Invalid check'

    def __call__(self, data):
        if self.checker(data):
            return data
        raise ValueError(self.message)


class Numbers(Pipeable):
    def __init__(self):
        self.empty = str_map('')
        self.re = str_map(r'\d+')

    def __call__(self, data):
        t = type(data)
        return self.empty[t].join(re.findall(self.re[t], data))


numbers = Numbers()


class Range(Pipeable):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, data):
        if self.min is not None and data < self.min:
            raise RangeException(data, min=self.min)
        if self.max is not None and data > self.max:
            raise RangeException(data, max=self.max)
        return data


irange = lambda min=None, max=None, base=None: Int(base=base) | Range(min, max)
frange = lambda min=None, max=None: float | Range(min, max)


class regex(Pipeable):
    def __init__(self, pattern, flags=0):
        self.re = re.compile(pattern, flags)

    def __call__(self, data):
        if not self.re.search(data):
            raise RegexException(data, self.re)
        return data


email = Str() | regex(r"(?i)^[A-Z0-9._%!#$%&'*+-/=?^_`{|}~()]+@[A-Z0-9]+([.-][A-Z0-9]+)*\.[A-Z]{2,22}$")

URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
url = Str() | regex(URL_REGEX)

uuid = Str() | regex(r"(?i)^(?:urn:uuid:)?\{?[a-f0-9]{8}(?:-?[a-f0-9]{4}){3}-?[a-f0-9]{12}\}?$")


class DateTime(Pipeable):
    def __init__(self, fmt='%Y-%m-%d %H:%M:%S'):
        self.fmt = fmt

    def __call__(self, data):
        return datetime.strptime(data, self.fmt)


def Date(fmt='%Y-%m-%d'):
    return DateTime(fmt) | (lambda r: r.date())


def Time(fmt='%H:%M:%S'):
    return DateTime(fmt) | (lambda r: r.time())


class Timestamp(Pipeable):
    def __init__(self, msec=False, utc=True):
        self.msec = msec
        self.utc = utc

    def __call__(self, data):
        data = float(data)
        if self.msec:
            data /= 1000

        if self.utc:
            return datetime.utcfromtimestamp(data)
        else:
            return datetime.fromtimestamp(data)


timestamp = Timestamp()
timestamp_msec = Timestamp(msec=True)


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


class oneof(Pipeable):
    def __init__(self, *alternatives):
        self.alternatives = alternatives
        self.blank = None

    def _adjust(self, typ):
        self.alternatives = [typ(a) for a in self.alternatives]
        blank = {}
        for a in self.alternatives:
            blank.update((k, None) for k in a.items)
        self.blank = blank
        return self

    def __call__(self, data):
        errors = []
        for idx, a in enumerate(self.alternatives):
            try:
                result = a(data)
            except Exception as e:
                errors.append((idx, e))
            else:
                if self.blank:
                    blank = self.blank.copy()
                    blank.update(result)
                    return blank
                return result

        raise Invalid([('one of', Invalid(errors, data))], data)


class MergedMap(Pipeable):
    def __init__(self, parts):
        self.parts = parts

    def __call__(self, data):
        result = {}
        for p in self.parts:
            result.update(p(data))
        return result


class AltMap(Map):
    def __init__(self, alt_maps, items):
        Map.__init__(self, items)
        self.alt_maps = [vars(m)['get'] for m in alt_maps]

    def get(self, data, item):
        for d, m in zip(data, self.alt_maps):
            if item.src in d:
                return m(self, d, item)


def make_schema(top_schema):
    def schema(*args, **kwargs):
        args = [r._adjust(top_schema) if isinstance(r, oneof) else top_schema(r)
                for r in args]

        tail = kwargs.pop('_', None)
        if args:
            if len(args) == 1 and not kwargs:
                s = args[0]
            else:
                if (issubclass(top_schema, Map)
                        and all(isinstance(r, top_schema) for r in args)):
                    arg_items = [r.items for r in args]
                    merged_items = merge_dicts(*arg_items, **kwargs)
                    s = top_schema(merged_items)
                else:
                    s = MergedMap(args + [top_schema(kwargs)])
        else:
            s = top_schema(kwargs)

        if tail:
            return s | tail

        return s

    schema.schema = top_schema
    return schema
