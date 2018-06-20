# -*- coding: utf-8 -*-
import os
import sys
import time
import json
from contextlib import contextmanager

import requests

from covador.compat import bstr
from . import helpers


@contextmanager
def server(covfile, module_name, append_coverage=False):
    pid = os.fork()
    if not pid:
        import coverage
        cov = coverage.Coverage(covfile, source=['covador'])
        cov._auto_load = append_coverage
        cov.start()
        print('Server starting...')
        try:
            __import__(module_name)
            module = sys.modules[module_name]
            module.main()
            print('Server stopped')
        except:
            import traceback
            traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        cov.stop()
        cov.save()
        os._exit(0)

    for _ in range(50):
        try:
            resp = requests.get('http://127.0.0.1:5000/status/')
            resp.content
        except:
            time.sleep(0.1)
        else:
            break
    else:
        raise Exception('Server did not start')

    try:
        yield
    finally:
        os.kill(pid, 2)
        wait_till = time.time() + 10
        killed = False
        while time.time() < wait_till:
            if os.waitpid(pid, os.WNOHANG) == (0, 0):
                time.sleep(0.3)
                os.kill(pid, 2)
            else:
                killed = True
                break

        if not killed:
            print('Server did not stoped on SIGINT, sending SIGKILL')
            os.kill(pid, 9)


def do_tests():
    # qs
    resp = requests.get('http://127.0.0.1:5000/qs/?boo=boo')
    assert resp.content == b'boo'

    # form
    resp = requests.post('http://127.0.0.1:5000/form/',
                         data={'p1': bstr(u'буу', 'utf-8'), 'p2': 10})
    assert resp.content == bstr(u'буу.10', 'utf-8')

    resp = requests.post('http://127.0.0.1:5000/form/',
                         data='p1=boo&p2=10')
    assert resp.status_code == 400
    assert resp.json() == {'details': {'p1': 'Required item',
                                       'p2': 'Required item'},
                           'error': 'bad-request'}

    # mform
    resp = requests.post('http://127.0.0.1:5000/form/',
                         data=helpers.mform,
                         headers={'Content-Type': helpers.mct})
    assert resp.content == bstr(u'буу.10', 'utf-8')

    # params
    resp = requests.post('http://127.0.0.1:5000/params/',
                         params={'p2': 10}, data={'p1': 'boo'})
    assert resp.content == b'boo.10'

    # args
    resp = requests.get('http://127.0.0.1:5000/args/boo/')
    assert resp.content == b'boo'

    # error
    resp = requests.get('http://127.0.0.1:5000/qs/')
    assert resp.status_code == 400
    assert resp.json() == {'details': {'boo': 'Required item'},
                           'error': 'bad-request'}

    # json body
    data = {'boo': 'утф'}
    resp = requests.post('http://127.0.0.1:5000/json/', json=data)
    assert resp.content == bstr(u'утф', 'utf-8')

    resp = requests.post('http://127.0.0.1:5000/json/', data=json.dumps(data))
    assert resp.status_code == 400
    assert resp.json() == {'details': {'boo': 'Required item'},
                           'error': 'bad-request'}


def test_flask():
    with server('flask.cov', 'integration.flask_server'):
        do_tests()


def test_tornado():
    with server('tornado.cov', 'integration.tornado_server'):
        do_tests()


def test_django():
    with server('django.cov', 'integration.django_server'):
        do_tests()

    with server('django.cov', 'integration.django_cbv_server', True):
        do_tests()


def test_aiohttp_async():
    with server('aiohttp_async.cov', 'integration.aiohttp_server'):
        do_tests()

    with server('aiohttp_async.cov', 'integration.aiohttp_cbv_server', True):
        do_tests()


def test_aiohttp_yield():
    with server('aiohttp_yield.cov', 'integration.aiohttp_yield_server'):
        do_tests()


def test_sanic():
    with server('sanic.cov', 'integration.sanic_server'):
        do_tests()

        resp = requests.get('http://127.0.0.1:5000/qs-multi/?boo=boo&boo=foo')
        assert resp.content == b'boo,foo'
