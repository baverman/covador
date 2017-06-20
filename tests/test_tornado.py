import sys

class tornado:
    web = None

sys.modules['tornado'] = tornado

from covador import tornado as cw
from covador import item, wrap_in


def test_simple():
    class Handler(object):
        class request:
            query_arguments = {'boo': [b'boo']}
            body_arguments = query_arguments

        @cw.query_string(cw.list_schema(boo='bytes') | wrap_in('raw'))
        @cw.query_string(cw.list_schema(boo=str) | wrap_in('data'))
        def get(self, data, raw):
            assert repr(data['boo']) == repr(u'boo')
            assert repr(raw['boo']) == repr(b'boo')

        @cw.form(boo=str, raw_boo=item('bytes', src='boo'))
        def post(self, boo, raw_boo):
            assert repr(boo) == repr(u'boo')
            assert repr(raw_boo) == repr(b'boo')

    Handler().get()
    Handler().post()
