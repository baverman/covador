from functools import wraps


class PipeMixin(object):
    def __or__(self, other):
        return Pipe([self, other])


class Pipe(PipeMixin):
    def __init__(self, items):
        self.items = items

    def __call__(self, data):
        for it in self.items:
            data = it(data)
        return data

    def __or__(self, other):
        return Pipe(self.items + [other])


class Item(object):
    def __init__(self, **params):
        self.__dict__.update(params)


def item(typ=None, source_key=None, required=True,
         default=None, multi=False, **kwargs):
    typ = wrap_type(typ)
    return Item(source_key=source_key, required=required,
                default=default, multi=multi, process=typ, **kwargs)


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
    if not isinstance(it, Item):
        it = item(it)
    return it


class Invalid(ValueError):
    def __init__(self, errors, valid):
        self.errors = errors
        self.valid = valid
        ValueError.__init__(self, repr(self.errors))


class Map(PipeMixin):
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
                if raw_data is None:
                    raise KeyError('None')
            except KeyError:
                if it.required:
                    errors.append((it.source_key, ValueError('Required field')))
                else:
                    result[k] = it.default
            else:
                try:
                    result[k] = it.process(raw_data)
                except Exception as e:
                    errors.append((it.source_key, e))

        if errors:
            raise Invalid(errors, result)

        return result


class List(PipeMixin):
    def __init__(self, item):
        self.item = get_item(item)

    def __call__(self, data):
        result = []
        errors = []
        rappend = result.append
        it = self.item
        for idx, raw_data in enumerate(data):
            if raw_data is None:
                if it.required:
                    rappend(None)
                    errors.append((idx, ValueError('Required field')))
                else:
                    rappend(it.default)
            else:
                try:
                    rappend(it.process(raw_data))
                except Exception as e:
                    rappend(None)
                    errors.append((idx, e))

        return result


class Tuple(PipeMixin):
    def __init__(self, items):
        self.items = [get_item(r) for r in items]

    def __call__(self, data):
        result = []
        errors = []
        rappend = result.append
        for idx, (it, raw_data) in enumerate(zip(self.items, data)):
            if raw_data is None:
                if it.required:
                    rappend(None)
                    errors.append((idx, ValueError('Required field')))
                else:
                    rappend(it.default)
            else:
                try:
                    rappend(it.process(raw_data))
                except Exception as e:
                    rappend(None)
                    errors.append((idx, e))

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


class Int(PipeMixin):
    def __init__(self, base=10):
        self.base = base

    def __call__(self, data):
        if type(data) is utype or type(data) is btype:
            return int(data, self.base)
        return int(data)


class Str(PipeMixin):
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


class Bytes(PipeMixin):
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def __call__(self, data):
        if type(data) is btype:
            return data
        elif type(data) is utype:
            return data.encode(self.encoding)
        else:
            return self(stype(data))


class split(PipeMixin):
    def __init__(self, item=None, separator=',', strip=True):
        self.separators = {
            utype: ustr(separator),
            btype: bstr(separator)
        }
        self.strip = strip
        self.list = item and List(item)

    def __call__(self, data):
        val = data.split(self.separators[type(data)])
        if self.strip:
            val = [r.strip() for r in val]

        if self.list:
            val = self.list(val)

        return val


def wrap_in(key):
    return lambda val: {key: val}


TYPES = {
    int: Int(),
    str: Str(),
    'bytes': Bytes(),
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
