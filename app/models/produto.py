import math

from app import database

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp"}


def extensao_permitida(nome_arquivo):
    """Confere se o arquivo de imagem tem uma extensão aceita."""
    if "." not in nome_arquivo:
        return False
    return nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS


def validar(dados):
    """Valida os dados do formulário.

    Retorna (dados_limpos, lista_de_erros).
    """
    erros = []

    nome = (dados.get("nome") or "").strip()
    especie = (dados.get("especie") or "").strip()
    descricao = (dados.get("descricao") or "").strip()
    preco_txt = (dados.get("preco") or "").strip().replace(",", ".")
    estoque_txt = (dados.get("estoque") or "").strip()

    if not nome:
        erros.append("Informe o nome do produto.")
    elif len(nome) > 100:
        erros.append("O nome pode ter no máximo 100 caracteres.")

    preco = None
    try:
        preco = float(preco_txt)
        if not math.isfinite(preco) or preco <= 0:
            erros.append("O preço deve ser maior que zero.")
    except ValueError:
        erros.append("Informe um preço válido, por exemplo 89,90.")

    estoque = 0
    if estoque_txt:
        try:
            estoque = int(estoque_txt)
            if estoque < 0:
                erros.append("O estoque não pode ser negativo.")
        except ValueError:
            erros.append("O estoque deve ser um número inteiro.")

    limpo = {
        "nome": nome,
        "especie": especie,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "imagem": None,
    }
    return limpo, erros


def listar():
    conn = database.get_connection()
    try:
        return conn.execute("SELECT * FROM produto ORDER BY nome").fetchall()
    finally:
        conn.close()


def buscar_por_id(produto_id):
    conn = database.get_connection()
    try:
        return conn.execute(
            "SELECT * FROM produto WHERE id = ?", (produto_id,)
        ).fetchone()
    finally:
        conn.close()


def criar(dados):
    conn = database.get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO produto (nome, especie, descricao, preco, estoque, imagem)
            VALUES (:nome, :especie, :descricao, :preco, :estoque, :imagem)
            """,
            dados,
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def atualizar(produto_id, dados):
    """Atualiza o produto. Se dados['imagem'] for None, mantém a imagem atual."""
    conn = database.get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE produto
            SET nome = :nome, especie = :especie, descricao = :descricao,
                preco = :preco, estoque = :estoque,
                imagem = COALESCE(:imagem, imagem)
            WHERE id = :id
            """,
            {**dados, "id": produto_id},
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def excluir(produto_id):
    conn = database.get_connection()
    try:
        cursor = conn.execute("DELETE FROM produto WHERE id = ?", (produto_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
