from .compat import utype, btype, stype, ustr, bstr
from .schema import Pipeable, get_item, Invalid, ALIASES, TYPES


class Map(Pipeable):
    def __init__(self, items):
        self.items = {}
        for k, it in items.items():
            it = get_item(it)
            if not it.source_key:
                it.source_key = k
            self.items[k] = it

    def get(self, data, item):
        return data[item.source_key]

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
    def get(self, data, field):
        if field.multi:
            return data[field.source_key]
        else:
            return data[field.source_key][0]


class Int(Pipeable):
    def __init__(self, base=None):
        self.base = base or 10

    def __call__(self, data):
        if type(data) is utype or type(data) is btype:
            return int(data, self.base)
        return int(data)


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


TYPES.update({
    dict: lambda it: Map(it),
    list: lambda it: List(it[0]),
    tuple: lambda it: Tuple(it),
})


ALIASES.update({
    int: Int(),
    'int': Int(),
    str: Str(),
    'str': Str(),
    'bytes': Bytes(),
})
