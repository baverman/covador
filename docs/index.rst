Covador
=======

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


* Support for flask, django, aiohttp and tornado.
* Simple creating of custom ``query_string``/``form``/``params``/``json_body``/``args`` wrappers.
* Multi dict support via item ``multi`` param.
* Multi dict keys support via item ``src`` param.
* Simple interface for custom validators/processors it's just a callable.
* Maps, Lists, Tuples, Enums.
* Validation chains: ``opt(default=[]) | split(separator=' ') | List(int) | (lambda it: it[:10])``
  or more concise ``opt(split(int, separator=' '), []) | operator.itemgetter(slice(10))`` —
  an optional argument of space separated integers and we need top 10 items from it and it
  is empty by default.
* Literal schema: ``schema(foo=[{'boo': int}])``, validates ``{'foo': [{'boo': 10}, {'boo': 20}]}``.
* Bytes/unicode aware.


Documentation
=============

.. toctree::
   :maxdepth: 1

   tutorial
   api

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
