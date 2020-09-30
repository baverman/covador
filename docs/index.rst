Covador
=======

Framework agnostic fast validation library.

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


* Support for flask (0.x, 1.0.x, 1.1.x), django (1.x, 2.x), aiohttp (2.x, 3.x),
  tornado (3.x, 4.x, 5.x, 6.x) and sanic (0.x, 18.x, 19.x).
* Simple creation of custom ``query_string``/``form``/``params``/``json_body``/``args`` wrappers.
* Multi dict support.
* Mapping from source to destination fields.
* Simple interface for custom validators/processors it's just a callable.
* Maps, typed Maps, Lists, Tuples, Enums.
* Validation chains::

     p = (opt(default=[]) | split(separator=' ')
          | List(int) | (lambda it: it[:10]))

  or more concise using nesting and ``operator.itemgetter``::

     p = (opt(split(int, separator=' '), [])
          | itemgetter(slice(10)))

  Explanationan: an optional argument of space separated integers and we need top 10 items from it and it
  is empty by default.
* Literal schemas::

     schema(foo=[{'boo': int}])

  validates ``{'foo': [{'boo': 10}, {'boo': 20}]}``.
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
