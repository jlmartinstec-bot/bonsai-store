import re

from app import database

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar(dados):
    """Valida os dados do formulário. Retorna (dados_limpos, lista_de_erros)."""
    erros = []

    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip().lower()
    telefone = (dados.get("telefone") or "").strip()
    endereco = (dados.get("endereco") or "").strip()

    if not nome:
        erros.append("Informe o nome do cliente.")
    elif len(nome) > 100:
        erros.append("O nome pode ter no máximo 100 caracteres.")

    if not email:
        erros.append("Informe o e-mail do cliente.")
    elif not EMAIL_REGEX.match(email):
        erros.append("Informe um e-mail válido, por exemplo nome@email.com.")

    limpo = {
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "endereco": endereco,
    }
    return limpo, erros


def listar():
    conn = database.get_connection()
    try:
        return conn.execute("SELECT * FROM cliente ORDER BY nome").fetchall()
    finally:
        conn.close()


def buscar_por_id(cliente_id):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT * FROM cliente WHERE id = ?", (cliente_id,)
        ).fetchone()
    finally:
        conn.close()


def criar(dados):
    conn = database.get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO cliente (nome, email, telefone, endereco)
            VALUES (:nome, :email, :telefone, :endereco)
            """,
            dados,
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def atualizar(cliente_id, dados):
    conn = database.get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE cliente
            SET nome = :nome, email = :email, telefone = :telefone,
                endereco = :endereco
            WHERE id = :id
            """,
            {**dados, "id": cliente_id},
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def excluir(cliente_id):
    conn = database.get_connection()
    try:
        cursor = conn.execute("DELETE FROM cliente WHERE id = ?", (cliente_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
