import sys; sys.path.insert(0, '.')

import json
import tornado.ioloop
import tornado.web
import tornado.gen

from covador import schema, item
from covador.tornado import query_string, json_body


class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    @query_string(foo=item(json.loads) | schema(boo=int), bar=item([int], multi=True))
    def get(self, foo, bar):
        self.write('foo is {0}, bar is {1}'.format(foo, bar))

    @tornado.gen.coroutine
    @json_body(foo=int, bar=[int])
    def post(self, foo, bar):
        self.write('foo is {0}, bar is {1}'.format(foo, bar))


def make_app():
    return tornado.web.Application([
        (r"/qs/", MainHandler),
        (r"/json/", MainHandler),
    ], debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    tornado.ioloop.IOLoop.current().start()
