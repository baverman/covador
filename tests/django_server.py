if __name__ == '__main__':
    import os, sys
    os.execlp('python', 'python',
              '-m', 'django',
              'runserver',
              '--pythonpath', '.',
              '--settings', 'tests.django_server',
              '127.0.0.1:5000')

import json

SECRET_KEY = 'boo'
DEBUG = True
ROOT_URLCONF = __name__
MIDDLEWARE = ()


from django.conf.urls import url
from django.http import HttpResponse

from covador import schema, item
from covador.django import query_string, json_body


@query_string(foo=item(json.loads) | schema(boo=int), bar=item([int], multi=True))
def test_qs(request, foo, bar):
    return HttpResponse('foo is {}, bar is {}'.format(foo, bar))


@json_body(foo=int, bar=[int])
def test_json(request, foo, bar):
    return HttpResponse('foo is {}, bar is {}'.format(foo, bar))


urlpatterns = [
    url(r'^qs/', test_qs),
    url(r'^json/', test_json),
]
