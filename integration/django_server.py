import sys; sys.path.insert(0, '.')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = __name__

SECRET_KEY = 'boo'
DEBUG = True
ROOT_URLCONF = __name__
MIDDLEWARE = ()
MIDDLEWARE_CLASSES = ()


from wsgiref import simple_server
from django.core.wsgi import get_wsgi_application
from django.conf.urls import url
from django.http import HttpResponse

from covador.django import query_string, json_body, form, params, rparams


@query_string(boo=str)
def qs_view(request, boo):
    return HttpResponse(boo)


@form(p1=str, p2=int)
def form_view(request, p1, p2):
    return HttpResponse(u'{0}.{1}'.format(p1, p2))


@params(p1=str, p2=int)
def params_view(request, p1, p2):
    return HttpResponse(u'{0}.{1}'.format(p1, p2))


@rparams(boo=str)
def rparams_view(request, boo):
    return HttpResponse(boo)


@json_body(boo=str)
def json_view(request, boo):
    return HttpResponse(boo)


urlpatterns = [
    url(r'^qs/', qs_view),
    url(r'^form/', form_view),
    url(r'^params/', params_view),
    url(r'^rparams/(?P<boo>.+)/', rparams_view),
    url(r'^json/', json_view),
]


def main():
    httpd = simple_server.make_server('127.0.0.1', 5000, get_wsgi_application())
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
