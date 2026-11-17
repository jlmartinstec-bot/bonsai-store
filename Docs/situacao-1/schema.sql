-- Projeto físico do banco de dados - Bonsai Store (SQLite)
-- Este script reproduz as tabelas criadas por app/database.py

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS produto (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT    NOT NULL,
    especie   TEXT,
    descricao TEXT,
    preco     REAL    NOT NULL CHECK (preco > 0),
    estoque   INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    imagem    TEXT
);

CREATE TABLE IF NOT EXISTS cliente (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome     TEXT NOT NULL,
    email    TEXT NOT NULL UNIQUE,
    telefone TEXT,
    endereco TEXT
);

CREATE TABLE IF NOT EXISTS pedido (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id  INTEGER NOT NULL,
    data_pedido TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    status      TEXT    NOT NULL DEFAULT 'Pendente',
    FOREIGN KEY (cliente_id) REFERENCES cliente (id)
);

CREATE TABLE IF NOT EXISTS item_pedido (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id      INTEGER NOT NULL,
    produto_id     INTEGER NOT NULL,
    quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario REAL    NOT NULL,
    FOREIGN KEY (pedido_id)  REFERENCES pedido (id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produto (id)
);
