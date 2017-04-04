import json


class Invalid(ValueError):
    def __init__(self, errors, clean):
        self.errors = errors
        self.clean = clean
        ValueError.__init__(self, repr(self.errors))


class RequiredExcepion(ValueError):
    def __str__(self):
        return 'Required item'


class EnumException(ValueError):
    def __init__(self, value, enum):
        self._value = value
        self._enum = enum

    def __str__(self):
        return '{} not in {}'.format(repr(self._value), self._enum)


class LengthException(ValueError):
    def __init__(self, value, min=None, max=None):
        self._value = value
        self._min = min
        self._max = max

    def __str__(self):
        size = len(self._value)
        if self._min is not None:
            return 'Length of {} is less then {}'.format(size, self._min)
        if self._max is not None:
            return 'Length of {} is greater then {}'.format(size, self._max)


class RangeException(ValueError):
    def __init__(self, value, min=None, max=None):
        self._value = value
        self._min = min
        self._max = max

    def __str__(self):
        if self._min is not None:
            return '{} is less then {}'.format(self._value, self._min)
        if self._max is not None:
            return '{} is greater then {}'.format(self._value, self._max)


class RegexException(ValueError):
    def __init__(self, value, regex):
        self._value = value
        self._regex = regex

    def __str__(self):
        return 'Mismatch "{}" for "{}"'.format(self._value, self._regex.pattern)


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
