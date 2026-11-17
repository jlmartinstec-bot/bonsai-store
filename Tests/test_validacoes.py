"""Testes unitários das regras de validação (não usam banco de dados)."""
from app.models import cliente, produto


def test_produto_valido():
    dados, erros = produto.validar(
        {"nome": "Bonsai Ficus", "preco": "89,90", "estoque": "5"}
    )
    assert erros == []
    assert dados["preco"] == 89.90
    assert dados["estoque"] == 5


def test_produto_sem_nome():
    _, erros = produto.validar({"nome": "  ", "preco": "10", "estoque": "1"})
    assert "Informe o nome do produto." in erros


def test_produto_preco_invalido():
    _, erros = produto.validar({"nome": "X", "preco": "abc", "estoque": "1"})
    assert any("preço válido" in e for e in erros)


def test_produto_preco_zero_ou_negativo():
    _, erros_zero = produto.validar({"nome": "X", "preco": "0"})
    _, erros_neg = produto.validar({"nome": "X", "preco": "-5"})
    assert any("maior que zero" in e for e in erros_zero)
    assert any("maior que zero" in e for e in erros_neg)


def test_produto_estoque_negativo_ou_texto():
    _, erros_neg = produto.validar({"nome": "X", "preco": "10", "estoque": "-1"})
    _, erros_txt = produto.validar({"nome": "X", "preco": "10", "estoque": "dois"})
    assert any("negativo" in e for e in erros_neg)
    assert any("inteiro" in e for e in erros_txt)


def test_produto_estoque_vazio_vira_zero():
    dados, erros = produto.validar({"nome": "X", "preco": "10", "estoque": ""})
    assert erros == []
    assert dados["estoque"] == 0


def test_extensoes_de_imagem():
    assert produto.extensao_permitida("foto.PNG")
    assert produto.extensao_permitida("bonsai.jpeg")
    assert not produto.extensao_permitida("virus.exe")
    assert not produto.extensao_permitida("semextensao")


def test_cliente_valido():
    dados, erros = cliente.validar({"nome": "Ana", "email": "ANA@Email.com"})
    assert erros == []
    assert dados["email"] == "ana@email.com"


def test_cliente_email_invalido_e_nome_vazio():
    _, erros = cliente.validar({"nome": "", "email": "ana-sem-arroba"})
    assert "Informe o nome do cliente." in erros
    assert any("e-mail válido" in e for e in erros)
