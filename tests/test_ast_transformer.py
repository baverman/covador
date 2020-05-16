from covador import validator_tpl
from covador.ast_transformer import transform


def test_simple():
    transform(validator_tpl, {'func': False, 'getter': False, 'validator': False})
