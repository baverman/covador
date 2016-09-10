import sys

import colander
from covador import Map, List, Tuple


class Friend(colander.TupleSchema):
    rank = colander.SchemaNode(colander.Int(),
                               validator=colander.Range(0, 9999))
    name = colander.SchemaNode(colander.String())


class Phone(colander.MappingSchema):
    location = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf(['home', 'work']))
    number = colander.SchemaNode(colander.String())


class Friends(colander.SequenceSchema):
    friend = Friend()


class Phones(colander.SequenceSchema):
    phone = Phone()


class Person(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    age = colander.SchemaNode(colander.Int(),
                              validator=colander.Range(0, 200))
    friends = Friends()
    phones = Phones()


schema = Person()


cs = Map({'name': str,
          'age': int,
          'friends': [(int, str)],
          'phones': [{'location': str, 'number': str}]})


cstruct = {
    'name': 'keith',
    'age': '20',
    'friends': [('1', 'jim'), ('2', 'bob'), ('3', 'joe'), ('4', 'fred')],
    'phones': [{'location': 'home', 'number': '555-1212'},
               {'location': 'work', 'number': '555-8989'}],
}


def test_colander():
    schema.deserialize(cstruct)


def test_covador():
    cs(cstruct)


if __name__ == '__main__':
    f = globals()[sys.argv[1]]
    for _ in xrange(50000):
        f()
