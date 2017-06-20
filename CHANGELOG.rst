dev
===

* [Break] Changed argument order for ``item``. ``default`` is on a second
  position now, so one can use ``opt(int, 0)`` instead of ``opt(int, default=0)``.
  Default values are more common case then custom source keys.

* [Feature] ``dest`` and ``src`` (an alias for ``source_key``) parameters for ``item``,
  it controls a destination and a source key value for a Map.

* [Feature] ``dpass`` decorator helper allows to use complex expression inline.

* [Feature] ``_`` keyword argument for schema constructor to attach a validation chain
  to a resulted schema. Can be used instead of ``dpass``.

* [Feature] Public properties for built-in validation exceptions.

* [Fix] Fixed ``covador.aiohttp.params`` decorator.

* [Fix] Incorrect schema for ``rparams`` for all supported frameworks.


0.9.1
=====

* [Feature] Exception hierarchy for built-in checkers.


0.9.0
=====

* Drop ``covador.aiohttp.m_*`` decorators in favor simple query_string/form/etc...
  Support for CBV are kept.

* Added json_body for django, tornado and aiohttp.

* Ability to customize error handler via ``.on_error`` validator decorator
  method:

  .. code:: python

      from covador import flask

      def error_handler(ctx):
          print ctx.exception
          ctx.reraise()  # reraise exception with original traceback

      custom_query_string = flask.query_string.on_error(error_handler)

* Pipeable decorators:

  .. code:: python

    from covador import wrap_in, flask

    pager = (flask.query_string(offset=int, limit=int)
             | (lambda d: Paginator(d['limit'], d['offset']))
             | wrap_in('pager'))

    @pager
    def view(pager):
        # use pager...
        pass
