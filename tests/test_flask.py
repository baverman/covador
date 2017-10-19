# -*- coding: utf-8 -*-
import json
from flask import Flask

from covador import opt
from covador.flask import *

from . import helpers

app = Flask(__name__)


def test_get_qs():
    @query_string(boo=opt(str))
    def test(boo):
        return boo

    with app.test_request_context(b'/?boo=boo'):
        assert test() == u'boo'
        assert request._covador_qs

    with app.test_request_context(b'/?boo='):
        assert test() == None
        assert request._covador_qs


def test_get_form():
    @form(boo=str)
    def test(boo):
        return boo

    @form(p1=str, p2=int)
    def mform(p1, p2):
        return p1, p2

    with app.test_request_context(b'/', data=b'boo=foo',
                                  content_type='application/x-www-form-urlencoded'):
        assert test() == u'foo'
        assert request._covador_form

    with app.test_request_context(b'/', data=helpers.mform, content_type=helpers.mct):
        assert mform() == (u'буу', 10)
        assert request._covador_form

    with app.test_request_context(b'/', data=b'boo='):
        resp = test()
        assert resp.status_code == 400

        error = json.loads(resp.get_data(True))
        assert error == {'details': {'boo': 'Required item'},
                         'error': 'bad-request'}


def test_get_params():
    @params(boo=str, foo=int)
    def test(boo, foo):
        return boo, foo

    with app.test_request_context(b'/?boo=baz', data=b'foo=10',
                                  content_type='application/x-www-form-urlencoded'):
        assert test() == (u'baz', 10)


def test_get_rparams():
    @rparams(boo=int)
    def test(boo):
        return boo

    with app.test_request_context(b'/?boo=baz', data=b'foo=10'):
        assert test(boo='10') == 10


def test_json():
    @json_body(boo=int, foo=str)
    def test(boo, foo):
        return boo, foo

    data = u'{"boo": "10", "foo": "утф"}'
    with app.test_request_context(b'/', data=data.encode('utf-8')):
        assert test() == (10, u'утф')
