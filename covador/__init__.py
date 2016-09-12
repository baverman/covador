from functools import wraps


class PipeMixin(object):
    def __or__(self, other):
        return Pipe([self, other])


Type = PipeMixin


class Pipe(PipeMixin):
    def __init__(self, pipe):
        self.pipe = pipe

    def __call__(self, data):
        for it in self.pipe:
            data = it(data)
        return data

    def __or__(self, other):
        return Pipe(self.pipe + [other])

    def __ror__(self, other):
        return Pipe([other] + self.pipe)


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


def wrap_type(typ):
    ttyp = type(typ)
    if ttyp is dict:
        return Map(typ)
    elif ttyp is list:
        return List(typ[0])
    elif ttyp is tuple:
        return Tuple(typ)

    return TYPES.get(typ, typ)


def get_item(it):
    if not isinstance(it, item):
        it = item(it)
    return it


class Invalid(ValueError):
    def __init__(self, errors, clean):
        self.errors = errors
        self.clean = clean
        ValueError.__init__(self, repr(self.errors))


class Map(Type):
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


class List(Type):
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


class Tuple(Type):
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


utype = type(u'')
btype = type(b'')
stype = type('')


def bstr(data):
    if type(data) is utype:
        data = data.encode('latin1')
    return data


def ustr(data):
    if type(data) is btype:
        data = data.decode('latin1')
    return data


class Int(Type):
    def __init__(self, base=10):
        self.base = base

    def __call__(self, data):
        if type(data) is utype or type(data) is btype:
            return int(data, self.base)
        return int(data)


class Str(Type):
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


class Bytes(Type):
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def __call__(self, data):
        if type(data) is btype:
            return data
        elif type(data) is utype:
            return data.encode(self.encoding)
        else:
            return self(stype(data))


class split(Type):
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
            val = filter(None, val)

        if self.list:
            val = self.list(val)

        return val


class enum(Type):
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


def wrap_in(key):
    return lambda val: {key: val}


TYPES = {
    int: Int(),
    str: Str(),
    'bytes': Bytes(),
    'str': Str(),
    'int': Int(),
    None: lambda it: it
}


def make_schema(top_schema):
    def schema(*args, **kwargs):
        if args:
            return args[0]
        return top_schema(kwargs)
    return schema


schema = make_schema(Map)


def make_validator(getter, on_error, top_schema=schema):
    def validator(*args, **kwargs):
        s = top_schema(*args, **kwargs)
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                data = getter(*args, **kwargs)
                try:
                    data = s(data)
                except Exception as e:
                    return on_error(e)
                else:
                    kwargs.update(data)
                    return func(*args, **kwargs)
            return inner
        return decorator
    return validator
