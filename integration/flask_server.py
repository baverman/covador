import sys; sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask
from covador.flask import query_string, json_body, form, params, rparams

app = Flask(__name__)
app._logger = logging.getLogger(__name__)


@app.route('/qs/')
@query_string(boo=str)
def qs_view(boo):
    return boo


@app.route('/form/', methods=['POST'])
@form(p1=str, p2=int)
def form_view(p1, p2):
    return u'{0}.{1}'.format(p1, p2)


@app.route('/params/', methods=['POST'])
@params(p1=str, p2=int)
def params_view(p1, p2):
    return u'{0}.{1}'.format(p1, p2)


@app.route('/rparams/<boo>/')
@rparams(boo=str)
def rparams_view(boo):
    return boo


@app.route('/json/', methods=['POST'])
@json_body(boo=str)
def json_view(boo):
    return boo


def main():
    app.run(debug=False)


if __name__ == '__main__':
    main()
