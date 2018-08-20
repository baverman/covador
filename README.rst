covador
=======

|travis| |coverage| |pyver|

.. |travis| image:: https://travis-ci.org/baverman/covador.svg?branch=master
   :target: https://travis-ci.org/baverman/covador

.. |coverage| image:: https://img.shields.io/badge/coverage-100%25-brightgreen.svg

.. |pyver| image:: https://img.shields.io/badge/python-2.6%2C_2.7%2C_3.4%2C_3.5%2C_3.6%2C_3.7%2C_pypy-blue.svg


Validation library for processing http endpoint arguments.


Usage
------------------

Flask
*****************

.. code:: python

    from flask import Flask

    from covador import split, opt
    from covador.flask import query_string

    app = Flask(__name__)

    @app.route('/')
    @query_string(foo=opt(split(int), []))
    def csv_argument(foo):
        return repr(foo)

    # GET /?foo=1,2,3 -> [1, 2, 3]

    if __name__ == '__main__':
        app.run()


Aiohttp
*****************

.. code:: python

    import ipaddress

    from aiohttp import web

    from covador import irange, item, length, opt
    from covador.aiohttp import json_body


    def ip_or_net(value):
        """Custom validation type.
        Raise ValueError if invalid type
        """
        value = value.strip()
        try:
            ipaddress.ip_address(value)
            return value
        except ValueError:
            pass
        ipaddress.ip_network(value)
        return value


    @json_body(
        # custom validation type, can be usual function that raises ValueError in case of
        # invalid values
        ip_address=[ip_or_net],
        # optional list field with automatically stripped strings with default empty list
        ids=opt([str.strip], []),
        # optional string field with default value 'API'
        source=opt(str, 'API'),
        # optional boolean field with default False
        bool_key=opt(bool, False),
        # optional integer field with allowed values from 0 to 6
        timeout=opt(irange(0, 6), None),
    )
    async def block(request, ip_address, ids, source, sync, timeout):
        """
        curl -X POST localhost:8080/api/v1/block \
        -H 'Content-Type: application/json' -d \
        '{"ids":["test  "],"ip_address":["101.12.123.123"],"timeout":2}'
        """
        return web.Response()


    def main():
        app = web.Application()
        app.add_routes([web.post('/api/v1/block', block)])
        web.run_app(app, host='127.0.0.1', port=8080)


    if __name__ == '__main__':
        main()


Literal schema
*****************

.. code:: python

    literal_schema = schema(
        # non empty required string field with minimum length of 1
        email=item(str, empty_is_none=False) | length(1, None),
        # optional enum type, only listed allowed default None
        platform=nopt(enum('iOS', 'Android'), None),
        # optional field with non negative integer and default value 0
        limit=opt(irange(min=0), 0),
        # optional string field with default empty string
        username=opt(str, ''),
    )

    try:
        validated = literal_schema({})
    except ValueError:
        # Error:
        # [('email', RequiredExcepion('Required item',))]
        pass


* Support for flask, django, aiohttp, tornado and sanic.
* Simple creating of custom ``query_string``/``form``/``params``/``json_body``/``args`` wrappers.
* Multi dict support via item ``multi`` param.
* Multi dict keys support via item ``src`` param.
* Simple interface for custom validators/processors it's just a callable.
* Maps, typed Maps, Lists, Tuples, Enums.
* Validation chains: ``opt(default=[]) | split(separator=' ') | List(int) | (lambda it: it[:10])``
  or more concise ``opt(split(int, separator=' '), []) | operator.itemgetter(slice(10))`` —
  an optional argument of space separated integers and we need top 10 items from it and it
  is empty by default.
* Literal schema: ``schema(foo=[{'boo': int}])``, validates ``{'foo': [{'boo': 10}, {'boo': 20}]}``.
* Bytes/unicode aware.
