from covador.ast_transformer import execute


def test_simple():
    execute('gen_validator.py',
            (('func', False), ('getter', False), ('validator', False)))
