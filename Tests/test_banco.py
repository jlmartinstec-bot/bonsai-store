"""Testa a criação do banco e a compatibilidade com bancos antigos."""
import sqlite3

from app import create_app, database


def test_cria_as_quatro_tabelas(app):
    conn = database.get_connection()
    tabelas = {
        linha["name"]
        for linha in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    conn.close()
    assert {"produto", "cliente", "pedido", "item_pedido"} <= tabelas


def test_banco_antigo_e_atualizado(tmp_path, monkeypatch):
    caminho = str(tmp_path / "antigo.db")
    monkeypatch.setattr(database, "DB_NAME", caminho)

    # banco da primeira versão: só 3 colunas
    conn = sqlite3.connect(caminho)
    conn.execute(
        "CREATE TABLE produto (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "nome TEXT NOT NULL, descricao TEXT, preco REAL NOT NULL)"
    )
    conn.execute("INSERT INTO produto (nome, descricao, preco) VALUES ('Antigo', 'x', 10.0)")
    conn.commit()
    conn.close()

    create_app({"TESTING": True, "UPLOAD_FOLDER": str(tmp_path / "uploads")})

    conn = database.get_connection()
    colunas = [linha["name"] for linha in conn.execute("PRAGMA table_info(produto)")]
    conn.close()
    assert {"especie", "estoque", "imagem"} <= set(colunas)
