import sys; sys.path.insert(0, '.')
import json

from flask import Flask

from covador import item, schema
from covador.flask import query_string, json_body

app = Flask(__name__)


@app.route('/qs/')
@query_string(foo=item(json.loads) | schema(boo=int), bar=item([int], multi=True))
def boo(foo, bar):
    return 'foo is {}, bar is {}'.format(foo, bar)


@app.route('/json/', methods=['POST'])
@json_body(foo=int, bar=[int])
def post(foo, bar):
    return 'foo is {}, bar is {}'.format(foo, bar)


if __name__ == '__main__':
    app.run(debug=True)
