import sys; sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from sanic import Sanic, response
from covador import item
from covador.sanic import query_string, json_body, form, params, args

app = Sanic()


@app.route('/qs/')
@query_string(boo=str)
async def qs_view(request, boo):
    return response.text(boo)


@app.route('/qs-multi/')
@query_string(boo=item(str, multi=True))
async def qs_multi_view(request, boo):
    return response.text(','.join(boo))


@app.route('/form/', methods=['POST'])
@form(p1=str, p2=int)
async def form_view(request, p1, p2):
    return response.text('{0}.{1}'.format(p1, p2))


@app.route('/params/', methods=['POST'])
@params(p1=str, p2=int)
async def params_view(request, p1, p2):
    return response.text('{0}.{1}'.format(p1, p2))


@app.route('/args/<boo>/')
@args(boo=str)
async def args_view(request, boo):
    return response.text(boo)


@app.route('/json/', methods=['POST'])
@json_body(boo=str)
async def json_view(request, boo):
    return response.text(boo)


def main():
    app.run(host='127.0.0.1', port=5000, debug=False)


if __name__ == '__main__':
    main()
