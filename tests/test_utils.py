from covador.utils import parse_qs


def test_parse_qs():
    assert parse_qs('boo=foo') == {'boo': ['foo']}
    assert parse_qs(b'boo=foo') == {'boo': [b'foo']}
