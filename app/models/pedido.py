from app import database

STATUS_VALIDOS = ["Pendente", "Pago", "Enviado", "Entregue"]


class EstoqueInsuficiente(ValueError):
    """Erro levantado quando não há estoque para atender o pedido."""


def criar_pedido(cliente_id, itens):
    """Registra o pedido e baixa o estoque, tudo numa única transação.

    itens: dicionário {produto_id: quantidade}
    Retorna o id do pedido criado.
    """
    if not itens:
        raise ValueError("O carrinho está vazio.")

    conn = database.get_connection()
    try:
        cliente = conn.execute(
            "SELECT id FROM cliente WHERE id = ?", (cliente_id,)
        ).fetchone()
        if cliente is None:
            raise ValueError("Cliente não encontrado.")

        cursor = conn.execute(
            "INSERT INTO pedido (cliente_id) VALUES (?)", (cliente_id,)
        )
        pedido_id = cursor.lastrowid

        for produto_id, quantidade in itens.items():
            item = conn.execute(
                "SELECT nome, preco, estoque FROM produto WHERE id = ?",
                (produto_id,),
            ).fetchone()

            if item is None:
                raise ValueError("Um dos produtos do carrinho não existe mais.")
            if item["estoque"] < quantidade:
                raise EstoqueInsuficiente(
                    f"Estoque insuficiente de {item['nome']} "
                    f"(disponível: {item['estoque']})."
                )

            conn.execute(
                """
                INSERT INTO item_pedido
                    (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (pedido_id, produto_id, quantidade, item["preco"]),
            )
            conn.execute(
                "UPDATE produto SET estoque = estoque - ? WHERE id = ?",
                (quantidade, produto_id),
            )

        conn.commit()
        return pedido_id

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar():
    conn = database.get_connection()
    try:
        return conn.execute(
            """
            SELECT p.id, p.data_pedido, p.status, c.nome AS cliente_nome,
                   COALESCE(SUM(i.quantidade * i.preco_unitario), 0) AS total
            FROM pedido p
            JOIN cliente c ON c.id = p.cliente_id
            LEFT JOIN item_pedido i ON i.pedido_id = p.id
            GROUP BY p.id
            ORDER BY p.id DESC
            """
        ).fetchall()
    finally:
        conn.close()


def buscar(pedido_id):
    """Devolve (pedido, itens, total). Se não existir, (None, [], 0.0)."""
    conn = database.get_connection()
    try:
        pedido = conn.execute(
            """
            SELECT p.*, c.nome AS cliente_nome, c.email AS cliente_email
            FROM pedido p
            JOIN cliente c ON c.id = p.cliente_id
            WHERE p.id = ?
            """,
            (pedido_id,),
        ).fetchone()

        if pedido is None:
            return None, [], 0.0

        itens = conn.execute(
            """
            SELECT i.quantidade, i.preco_unitario, pr.nome,
                   (i.quantidade * i.preco_unitario) AS subtotal
            FROM item_pedido i
            JOIN produto pr ON pr.id = i.produto_id
            WHERE i.pedido_id = ?
            """,
            (pedido_id,),
        ).fetchall()

        total = sum(item["subtotal"] for item in itens)
        return pedido, itens, total
    finally:
        conn.close()


def atualizar_status(pedido_id, status):
    if status not in STATUS_VALIDOS:
        raise ValueError("Status inválido.")

    conn = database.get_connection()
    try:
        cursor = conn.execute(
            "UPDATE pedido SET status = ? WHERE id = ?", (status, pedido_id)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
