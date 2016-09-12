covador
=======

Validation library for processing http endpoint arguments.

.. code:: python

    from flask import Flask

    from covador import split, opt
    from covador.flask import query_string

    app = Flask(__name__)

    @app.route('/')
    @query_string(foo=opt(split(int), default=[]))
    def csv_argument(foo):
        return repr(foo)

    # GET /?foo=1,2,3 -> [1, 2, 3]

    if __name__ == '__main__':
        app.run()


* Support for flask, django and tornado.
* Simple creating of custom ``query_sttring``/``form``/``params`` wrappers.
* Multi dict support via item ``multi`` param.
* Multi dict keys support vial item ``source_key`` param.
* Simple interface for custom validators/processors it's just a callable.
* Maps, Lists, Tuples, Enums.
* Validation chains: ``opt(default=[]) | split(separator=' ') | List(int) | (lambda it: it[:10])`` —
  optional argument space separated integers and we need top 10 items from it.
* Literal schema: ``schema(foo=[{'boo': int}])``, validates ``{'foo': [{'boo': 10}, {'boo': 20}]}``.
* Build-in splitter.
* byte/unicode aware.
* py2/py3 compatible.
