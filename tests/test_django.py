# -*- coding: utf-8 -*-
import os
os.environ['DJANGO_SETTINGS_MODULE'] = __name__

import json
from webob import Request as TRequest
from django.core.handlers.wsgi import WSGIRequest

from covador import opt
from covador.django import *

from . import helpers

SECRET_KEY = 'boo'


def make_request(*args, **kwargs):
    return WSGIRequest(TRequest.blank(*args, **kwargs).environ)


def test_query_string():
    @query_string(boo=str)
    def test(request, boo):
        return boo

    request = make_request('/?boo=boo')
    assert test(request) == u'boo'
    assert request._covador_qs


def test_form():
    @form(boo=str)
    def test(request, boo):
        return boo

    request = make_request('/', POST=b'boo=boo')
    assert test(request) == u'boo'
    assert request._covador_form


def test_mform():
    @form(p1=str, p2=int)
    def test(request, p1, p2):
        return p1, p2

    request = make_request('/', POST=helpers.mform, content_type=helpers.mct)
    assert test(request) == (u'буу', 10)
    assert request._covador_form


def test_params():
    @params(boo=str, foo=int)
    def test(request, boo, foo):
        return boo, foo

    request = make_request('/?boo=boo', POST=b'foo=10')
    assert test(request) == (u'boo', 10)

    request = make_request('/?boo=boo&foo=10')
    assert test(request) == (u'boo', 10)


def test_rparams():
    @rparams(boo=str)
    def test(request, boo):
        return boo

    request = make_request('/?boo=boo', POST=b'foo=10')
    assert test(request, boo='boo') == u'boo'


def test_error():
    @query_string(boo=str)
    def test(request, boo):
        return boo

    resp = test(make_request('/?boo='))
    assert resp.status_code == 400

    error = json.loads(resp.content.decode('utf-8'))
    assert error == {'details': {'boo': 'Required item'},
                     'error': 'bad-request'}


def test_json_body():
    @json_body(boo=opt(str))
    def test(request, boo):
        return boo

    data = u'{"boo": "утф"}'.encode('utf-8')
    assert test(make_request('/', POST=data, content_type='application/json')) == u'утф'
    assert test(make_request('/', POST=b'')) == None
