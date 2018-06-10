import sys; sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

import json
import tornado.ioloop
import tornado.web
import tornado.gen

from covador import schema, item
from covador.tornado import query_string, json_body, form, params, rparams


class QSHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    @query_string(boo=str)
    def get(self, boo):
        self.write(boo)


class FormHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    @form(p1=str, p2=int)
    def post(self, p1, p2):
        self.write(u'{0}.{1}'.format(p1, p2))


class ParamsHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    @params(p1=str, p2=int)
    def post(self, p1, p2):
        self.write(u'{0}.{1}'.format(p1, p2))


class RParamsHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    @rparams(boo=str)
    def get(self, boo):
        self.write(boo)


class JsonHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    @json_body(boo=str)
    def post(self, boo):
        self.write(boo)


def make_app():
    return tornado.web.Application([
        (r"/qs/", QSHandler),
        (r"/form/", FormHandler),
        (r"/params/", ParamsHandler),
        (r"/rparams/(?P<boo>.+)/", RParamsHandler),
        (r"/json/", JsonHandler),
    ], debug=False)


def main():
    app = make_app()
    app.listen(5000)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
