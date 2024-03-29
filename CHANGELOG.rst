0.10.2
======

* [Fix] Do not parse semicolons in urlencoded POST body


0.10.1
======

* [Fix] error_to_dict fail on BadField error.


0.10
====

* [Break] ``covador.aiohttp.AsyncValidationDecorator`` removed in favour of unified
  sync/async through AST transformation (``_async/gen_validator.py``).
* [Feature] python 3.8 support.
* [Feature] view function can raise ``covador.errors.Invalid`` exception and
  covador will handle it with an appropriate error handler.
* [Fix] use AST transformer to get legacy and new style coroutines for
  ``covador.aiohttp.get_form`` and ``covador.aiohttp.get_json``. Fixes
  ``@coroutine`` deprecation warning in python3.8.


0.9.26
======

* [Fix] Right hand pipe must coerce value to item.


0.9.25
======

* [Feature] web frameworks in integration tests were updated.
* [Fix] aiohttp query_string decorator led to deprecation error.


0.9.24
======

* [Fix] length(min=N) was treated as length(N) -- sequence must
  have length of N exactly. This is confusing and wrong behavior.


0.9.23
======

* [Refactor] extract item getter entity from `Map`.
* [Feature] soft map type. It can describe dicts with
  unknown keys.
* [Fix] One can pass pipes with maps into schema.


0.9.22
======

* Schema introspection for view functions

  .. code:: python

    import covador
    from covador.flask import query_string

    @query_string(boo=int)
    def view():
        pass

    print(view.schema.items)
    # {'boo': <covador.types.item object at 0x7fb2c9dad208>}


0.9.21
======

* [Feature] python 3.7 support
* [Optimization] `schema(...)` tries to return Map with merged items
  instead of `MergedMap`.


0.9.20
======

* [Break] `rparams` renamed to `args`.
* [Fix] aiohttp and sanic.
* [Refactor] Real integration tests with whole app starting.


0.9.18
======

* [Feature] python 2.6 support
* [Fix] missing pipeable support for ``oneof``.
* [Fix] django support


0.9.17
======

* [Fix] Ensure ``List`` validator for items with ``multi=True``.


0.9.16
======

* [Break] IMPORTANT!! ``empty_is_none`` consider empty strings only. For example,
  ``schema(price=int)({'price': 0})`` does not raises Required Item exception
  anymore.

* [Feature/Break] Strict parsing for ``application/x-www-form-urlencoded``,
  ``multipart/form-data`` and ``application/json`` content types.

* [Feature] ``covador.vdecorator.mergeof`` validation decorator compositor.
  For example, all ``params`` decorators are ``mergeof(query_string, form)``.

* [Feature] Support for ``multipart/form-data`` content type.

* [Feature] Assume empty dictionary for ``json_body`` in case of empty request body.

* [Feature] ``covador.check`` allows to create validators from boolean functions.

* [Feature] Log invalid inputs for validation decorators. One can use
  ``COVADOR_DEBUG`` environment variable to enable stack traces in logs.

* [Refactor] Extract ``covador.vdecorator`` module from ``covador.utils``.


0.9.15
======

* [Break] empty_is_none=True for ``covador.item`` to synchronize behavior with ``covador.opt``.
  Introduce similar ``covador.nitem``. Change allows to make explicit empty values acceptance.

0.9.14
======

* [Fix] Common item declarations lead to field erasure in schema.


0.9.13
======

* [Feature] Add support for Sanic.


0.9.12
======

* [Feature] ``KeyVal`` validator for typed mappings like Map<T1,T2>.


0.9.11
======

* [Fix] reimplementation of parse_qs to deal with bug in py3.


0.9.10
=====

* [Fix] UnicodeDecodeError in parse_qs under python3.


0.9.8
=====

* [Break] rename ``t_date``, ``t_time``, ``t_datetime`` into ``Date``, ``Time``,
  ``DateTime`` respectively.

* [Feature] ``aiohttp.rparams`` now uses ``request.match_info``.


0.9.7
=====

* [Break] ``length`` validator with single argument asumes min=max, so
  ``length(3) is equivalent for length(3, 3)``.

* [Feature] ``numbers`` validator which can extract number sequences from
  strings. Can be used to extract digits from phone numbers.


0.9.6
=====

* [Feature] Naive ``t_datetime``, ``t_date`` and ``t_time`` validators.
  Completely timezone-unaware. Suitable only for simple cases when only
  a local time is needed. And you always can apply pytz for these values.

* [Feature] ``timestamp`` validator to deal with unix timestamps in seconds
  and milliseconds and treat it like UTC and local values.

* [Feature] Error handler wrapper allows to override default error handlers
  without touching decorators:

  .. code:: python

      from covador import flask

      @flask.error_hanler.set
      def custom_error_handler(ctx):
          print ctx.exception
          ctx.reraise()  # reraise exception with original traceback


0.9.5
=====

* [Break] Changed argument order for ``item``. ``default`` is on a second
  position now, so one can use ``opt(int, 0)`` instead of ``opt(int, default=0)``.
  Default values are more common case then custom source keys.

* [Feature] ``oneof`` validator to select suitable alternative.

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
