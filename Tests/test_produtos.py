"""Testes de integração do cadastro de produtos (rotas + banco temporário)."""
import io

from app import database


def _id_produto(nome):
    conn = database.get_connection()
    try:
        return conn.execute("SELECT id FROM produto WHERE nome = ?", (nome,)).fetchone()["id"]
    finally:
        conn.close()


def test_vitrine_mostra_produtos_de_exemplo(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert b"Bonsai Ficus" in resposta.data
    assert b"Adicionar ao carrinho" in resposta.data


def test_cadastrar_produto(client):
    resposta = client.post(
        "/produtos/novo",
        data={"nome": "Bonsai Teste", "especie": "Ficus", "preco": "80,50", "estoque": "5"},
        follow_redirects=True,
    )
    assert b"cadastrado com sucesso" in resposta.data
    assert "R$ 80,50".encode() in resposta.data


def test_cadastrar_produto_com_erros(client):
    resposta = client.post(
        "/produtos/novo", data={"nome": "Teste", "preco": "abc", "estoque": "-1"}
    )
    assert "preço válido".encode() in resposta.data
    assert b"negativo" in resposta.data
    assert b'value="abc"' in resposta.data  # formulário mantém o que foi digitado


def test_editar_produto(client):
    produto_id = _id_produto("Bonsai Ficus")
    resposta = client.post(
        f"/produtos/{produto_id}/editar",
        data={"nome": "Bonsai Ficus Editado", "preco": "95,5", "estoque": "3"},
        follow_redirects=True,
    )
    assert b"atualizado com sucesso" in resposta.data
    assert b"Bonsai Ficus Editado" in resposta.data
    assert "R$ 95,50".encode() in resposta.data


def test_editar_produto_inexistente_da_404(client):
    assert client.get("/produtos/9999/editar").status_code == 404


def test_excluir_produto(client):
    produto_id = _id_produto("Bonsai Carmona")
    resposta = client.post(f"/produtos/{produto_id}/excluir", follow_redirects=True)
    assert "Produto excluído".encode() in resposta.data
    assert b"Bonsai Carmona" not in resposta.data


def test_upload_de_imagem_valida(client, app):
    resposta = client.post(
        "/produtos/novo",
        data={
            "nome": "Bonsai Com Foto",
            "preco": "100",
            "estoque": "1",
            "imagem": (io.BytesIO(b"conteudo-de-imagem"), "foto.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"cadastrado com sucesso" in resposta.data
    assert b"/static/uploads/" in resposta.data


def test_upload_de_arquivo_nao_permitido(client):
    resposta = client.post(
        "/produtos/novo",
        data={
            "nome": "Bonsai Falso",
            "preco": "100",
            "imagem": (io.BytesIO(b"programa"), "virus.exe"),
        },
        content_type="multipart/form-data",
    )
    assert b"PNG, JPG, GIF ou WEBP" in resposta.data
    assert b"Bonsai Falso" in resposta.data  # continua no formulario


def test_pagina_inexistente_da_404(client):
    resposta = client.get("/pagina-que-nao-existe")
    assert resposta.status_code == 404
    assert b"Erro 404" in resposta.data
