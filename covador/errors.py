import json


class Invalid(ValueError):
    def __init__(self, errors, clean):
        self.errors = errors
        self.clean = clean
        ValueError.__init__(self, repr(self.errors))


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
    return json.dumps(data, sort_keys=True,
                      ensure_ascii=False, indent=4).encode(encoding)
