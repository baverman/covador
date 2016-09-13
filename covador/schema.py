ALIASES = {
    None: lambda it: it
}
TYPES = {}


def wrap_type(typ):
    t = TYPES.get(type(typ))
    if t:
        return t(typ)

    return ALIASES.get(typ, typ)


class Pipeable(object):
    def __or__(self, other):
        return Pipe([self, other])

    def __ror__(self, other):
        return Pipe([other, self])


class Pipe(Pipeable):
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


def get_item(it):
    if not isinstance(it, item):
        it = item(it)
    return it


def make_schema(top_schema):
    def schema(*args, **kwargs):
        if args:
            return args[0]
        return top_schema(kwargs)
    return schema


class Invalid(ValueError):
    def __init__(self, errors, clean):
        self.errors = errors
        self.clean = clean
        ValueError.__init__(self, repr(self.errors))
