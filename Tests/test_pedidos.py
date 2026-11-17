"""Testes do fluxo completo: carrinho -> pedido -> baixa de estoque."""
from app import database


def _estoque(produto_id):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT estoque FROM produto WHERE id = ?", (produto_id,)
        ).fetchone()["estoque"]
    finally:
        conn.close()


def _cadastrar_cliente(client):
    client.post("/clientes/novo", data={"nome": "Ana", "email": "ana@email.com"})


def test_carrinho_vazio_e_recusado(client):
    _cadastrar_cliente(client)
    resposta = client.post("/carrinho/finalizar", data={"cliente_id": "1"}, follow_redirects=True)
    assert "carrinho está vazio".encode() in resposta.data


def test_adicionar_ao_carrinho(client):
    resposta = client.post("/carrinho/adicionar/1", follow_redirects=True)
    assert b"adicionado ao carrinho" in resposta.data
    assert b"Bonsai Ficus" in client.get("/carrinho/").data


def test_nao_adiciona_mais_que_o_estoque(client):
    for _ in range(10):  # estoque do Bonsai Ficus é 10
        client.post("/carrinho/adicionar/1")
    resposta = client.post("/carrinho/adicionar/1", follow_redirects=True)
    assert b"Estoque insuficiente" in resposta.data


def test_remover_do_carrinho(client):
    client.post("/carrinho/adicionar/1")
    resposta = client.post("/carrinho/remover/1", follow_redirects=True)
    assert b"removido do carrinho" in resposta.data
    assert "carrinho está vazio".encode() in resposta.data


def test_finalizar_pedido_baixa_o_estoque(client):
    _cadastrar_cliente(client)
    client.post("/carrinho/adicionar/1")
    client.post("/carrinho/adicionar/1")
    client.post("/carrinho/adicionar/2")

    resposta = client.post("/carrinho/finalizar", data={"cliente_id": "1"}, follow_redirects=True)

    assert b"Pedido realizado com sucesso" in resposta.data
    assert "R$ 309,70".encode() in resposta.data  # 2 x 89,90 + 129,90
    assert _estoque(1) == 8
    assert _estoque(2) == 5
    assert "carrinho está vazio".encode() in client.get("/carrinho/").data


def test_finalizar_sem_escolher_cliente(client):
    client.post("/carrinho/adicionar/1")
    resposta = client.post("/carrinho/finalizar", data={"cliente_id": ""}, follow_redirects=True)
    assert b"Escolha o cliente" in resposta.data


def test_estoque_insuficiente_desfaz_o_pedido(client):
    _cadastrar_cliente(client)
    client.post("/carrinho/adicionar/1")

    # outra pessoa esvazia o estoque antes de finalizar
    conn = database.get_connection()
    conn.execute("UPDATE produto SET estoque = 0 WHERE id = 1")
    conn.commit()
    conn.close()

    resposta = client.post("/carrinho/finalizar", data={"cliente_id": "1"}, follow_redirects=True)
    assert b"Estoque insuficiente" in resposta.data
    assert b"Nenhum pedido" in client.get("/pedidos/").data  # nada foi gravado


def test_alterar_status_do_pedido(client):
    _cadastrar_cliente(client)
    client.post("/carrinho/adicionar/1")
    client.post("/carrinho/finalizar", data={"cliente_id": "1"})

    resposta = client.post("/pedidos/1/status", data={"status": "Pago"}, follow_redirects=True)
    assert b"Status do pedido atualizado" in resposta.data

    resposta = client.post("/pedidos/1/status", data={"status": "Inventado"}, follow_redirects=True)
    assert "Status inválido".encode() in resposta.data


def test_pedido_inexistente_da_404(client):
    assert client.get("/pedidos/999").status_code == 404


def test_nao_exclui_cliente_nem_produto_com_pedido(client):
    _cadastrar_cliente(client)
    client.post("/carrinho/adicionar/1")
    client.post("/carrinho/finalizar", data={"cliente_id": "1"})

    resposta = client.post("/clientes/1/excluir", follow_redirects=True)
    assert b"j\xc3\xa1 tem pedidos" in resposta.data

    resposta = client.post("/produtos/1/excluir", follow_redirects=True)
    assert "já está em pedidos".encode() in resposta.data
