from covador import schema, item, nitem
from covador.errors import error_to_dict, error_to_json


def test_error_to_dict():
    s = schema(foo=nitem(schema(boo=int)), bar=item([int]))

    try:
        s({'foo': {}, 'bar': [1, 'a']})
    except Exception as e:
        errors = error_to_dict(e)
        assert errors == {'foo': {'boo': 'Required item'}, 'bar': {1: "invalid literal for int() with base 10: 'a'"}}

        json = error_to_json(e)
