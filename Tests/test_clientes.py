"""Testes de integração do cadastro de clientes."""


def _cadastrar(client, nome="Ana", email="ana@email.com"):
    return client.post(
        "/clientes/novo",
        data={"nome": nome, "email": email, "telefone": "61999999999"},
        follow_redirects=True,
    )


def test_cadastrar_cliente(client):
    resposta = _cadastrar(client)
    assert b"Cliente cadastrado com sucesso" in resposta.data
    assert b"ana@email.com" in resposta.data


def test_email_duplicado_e_recusado(client):
    _cadastrar(client)
    resposta = _cadastrar(client, nome="Outra Ana")
    assert "já existe um cliente".encode() in resposta.data.lower()


def test_cliente_com_email_invalido(client):
    resposta = client.post("/clientes/novo", data={"nome": "Ana", "email": "ana"})
    assert "e-mail válido".encode() in resposta.data


def test_editar_e_excluir_cliente(client):
    _cadastrar(client)
    resposta = client.post(
        "/clientes/1/editar",
        data={"nome": "Ana Maria", "email": "ana@email.com"},
        follow_redirects=True,
    )
    assert b"Ana Maria" in resposta.data

    resposta = client.post("/clientes/1/excluir", follow_redirects=True)
    assert b"Cliente exclu" in resposta.data
    assert b"Ana Maria" not in resposta.data
