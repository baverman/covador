from covador.ast_transformer import import_module


def test_simple():
    params = (('func', False), ('getter', False), ('validator', False))
    import_module('covador.gen_validator_t', params)
    from covador import gen_validator_t
    assert gen_validator_t.params == params
    assert gen_validator_t.gen_validator

