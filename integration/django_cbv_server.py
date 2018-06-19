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
from django.views.generic import View

from covador.django import m_query_string, m_form, m_params, m_args, m_json_body


class QS(View):
    @m_query_string(boo=str)
    def get(self, request, boo):
        return HttpResponse(boo)


class Form(View):
    @m_form(p1=str, p2=int)
    def post(self, request, p1, p2):
        return HttpResponse(u'{0}.{1}'.format(p1, p2))


class Params(View):
    @m_params(p1=str, p2=int)
    def post(self, request, p1, p2):
        return HttpResponse(u'{0}.{1}'.format(p1, p2))


class Args(View):
    @m_args(boo=str)
    def get(self, request, boo):
        return HttpResponse(boo)


class JSON(View):
    @m_json_body(boo=str)
    def post(self, request, boo):
        return HttpResponse(boo)


urlpatterns = [
    url(r'^qs/', QS.as_view()),
    url(r'^form/', Form.as_view()),
    url(r'^params/', Params.as_view()),
    url(r'^args/(?P<boo>.+)/', Args.as_view()),
    url(r'^json/', JSON.as_view()),
]


def main():
    httpd = simple_server.make_server('127.0.0.1', 5000, get_wsgi_application())
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
