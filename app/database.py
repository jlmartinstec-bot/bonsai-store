import os
import sqlite3

# Pasta principal do projeto (uma acima da pasta "app")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminho do banco de dados
DB_NAME = os.path.join(BASE_DIR, "bonsai.db")


def get_connection():
    """Abre a conexão com o banco, com chaves estrangeiras ligadas."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _colunas(conn, tabela):
    return [linha["name"] for linha in conn.execute(f"PRAGMA table_info({tabela})")]


def inicializar_banco():
    """Cria as tabelas (se não existirem) e cadastra produtos de exemplo."""
    conn = get_connection()

    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS produto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                especie TEXT,
                descricao TEXT,
                preco REAL NOT NULL CHECK (preco > 0),
                estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
                imagem TEXT
            );

            CREATE TABLE IF NOT EXISTS cliente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                telefone TEXT,
                endereco TEXT
            );

            CREATE TABLE IF NOT EXISTS pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                data_pedido TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                status TEXT NOT NULL DEFAULT 'Pendente',
                FOREIGN KEY (cliente_id) REFERENCES cliente (id)
            );

            CREATE TABLE IF NOT EXISTS item_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                preco_unitario REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedido (id) ON DELETE CASCADE,
                FOREIGN KEY (produto_id) REFERENCES produto (id)
            );
        """)

        # Compatibilidade: bancos criados nas versões anteriores
        colunas = _colunas(conn, "produto")
        if "especie" not in colunas:
            conn.execute("ALTER TABLE produto ADD COLUMN especie TEXT")
        if "estoque" not in colunas:
            conn.execute(
                "ALTER TABLE produto ADD COLUMN estoque INTEGER NOT NULL DEFAULT 0"
            )
        if "imagem" not in colunas:
            conn.execute("ALTER TABLE produto ADD COLUMN imagem TEXT")

        # Insere produtos de exemplo somente se a tabela estiver vazia
        quantidade = conn.execute("SELECT COUNT(*) FROM produto").fetchone()[0]

        if quantidade == 0:
            produtos = [
                (
                    "Bonsai Ficus",
                    "Ficus",
                    "Bonsai ideal para ambientes internos, de fácil manutenção.",
                    89.90,
                    10,
                ),
                (
                    "Bonsai Junípero",
                    "Junípero",
                    "Bonsai de estilo clássico, indicado para cultivo externo.",
                    129.90,
                    6,
                ),
                (
                    "Bonsai Carmona",
                    "Carmona",
                    "Bonsai ornamental com folhas pequenas e delicadas.",
                    99.90,
                    8,
                ),
            ]

            conn.executemany(
                """
                INSERT INTO produto (nome, especie, descricao, preco, estoque)
                VALUES (?, ?, ?, ?, ?)
                """,
                produtos,
            )

        conn.commit()

    finally:
        conn.close()
