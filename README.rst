covador
=======

|travis| |coverage| |pyver|

.. |travis| image:: https://travis-ci.org/baverman/covador.svg?branch=master
   :target: https://travis-ci.org/baverman/covador

.. |coverage| image:: https://img.shields.io/badge/coverage-100%25-brightgreen.svg

.. |pyver| image:: https://img.shields.io/badge/python-2.6%2C_2.7%2C_3.4%2C_3.5%2C_3.6%2C_3.7%2C_3.8%2C_pypy-blue.svg


Validation library for processing http endpoint arguments.

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


* Support for flask(0.x, 1.0.x, 1.1.x), django(1.x, 2.x), aiohttp(2.x, 3.x),
  tornado(3.x, 4.x, 5.x, 6.x) and sanic(0.x, 18.x, 19.x).
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
