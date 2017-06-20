import json


class Invalid(ValueError):
    def __init__(self, errors, clean):
        self.errors = errors
        self.clean = clean
        ValueError.__init__(self, repr(self.errors))


class RequiredExcepion(ValueError):
    def __init__(self, message=None):
        ValueError.__init__(self, message or 'Required item')


class EnumException(ValueError):
    def __init__(self, value, enum):
        self.value = value
        self.enum = enum
        ValueError.__init__(self, '{} not in {}'.format(repr(value), enum))


class LengthException(ValueError):
    def __init__(self, value, min=None, max=None):
        self.value = value
        self.min = min
        self.max = max

        size = len(value or '')
        if min is not None:
            ValueError.__init__(self, 'Length of {} is less then {}'.format(size, min))
        else:
            ValueError.__init__(self, 'Length of {} is greater then {}'.format(size, max))


class RangeException(ValueError):
    def __init__(self, value, min=None, max=None):
        self.value = value
        self.min = min
        self.max = max

        if min is not None:
            ValueError.__init__(self, '{} is less then {}'.format(value, min))
        else:
            ValueError.__init__(self, '{} is greater then {}'.format(value, max))


class RegexException(ValueError):
    def __init__(self, value, regex):
        self.value = value
        self.regex = regex
        ValueError.__init__(self, 'Mismatch "{}" for "{}"'.format(value, regex.pattern))


def error_to_dict(exc):
    if isinstance(exc, Invalid):
        return {key: error_to_dict(error) for key, error in exc.errors}
    else:
        return str(exc)


DEFAULT_ROOT = {'error': 'bad-request'}
DEFAULT_FIELD = 'details'


def error_to_json(exc, root=None, field=None, encoding='utf-8'):
    data = (root or DEFAULT_ROOT).copy()
    data[field or DEFAULT_FIELD] = error_to_dict(exc)
    return json.dumps(data, sort_keys=True, ensure_ascii=False, indent=4).encode(encoding)
