0.9.0
=====

* Drop `covador.aiohttp.m_*` decorators in favor simple query_string/form/etc...
  Support for CBV are kept.

* Added json_body for django, tornado and aiohttp.

* Ability to customize error handler via `.on_error` validator decorator
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
