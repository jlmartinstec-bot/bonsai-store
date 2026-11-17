from app.models import produto


def adicionar(carrinho, produto_id):
    """Adiciona 1 unidade do produto ao carrinho (um dicionário {id: quantidade}).

    Levanta ValueError se o produto não existir ou não tiver estoque.
    """
    item = produto.buscar_por_id(produto_id)
    if item is None:
        raise ValueError("Produto não encontrado.")

    chave = str(produto_id)
    atual = carrinho.get(chave, 0)
    if item["estoque"] <= atual:
        raise ValueError(f"Estoque insuficiente de {item['nome']}.")

    carrinho[chave] = atual + 1


def remover(carrinho, produto_id):
    """Tira o produto do carrinho (se ele estiver lá)."""
    carrinho.pop(str(produto_id), None)


def itens_detalhados(carrinho):
    """Devolve (lista_de_itens, total) para mostrar o carrinho na tela."""
    itens = []
    total = 0.0

    for chave, quantidade in carrinho.items():
        item = produto.buscar_por_id(int(chave))
        if item is None:
            continue
        subtotal = item["preco"] * quantidade
        itens.append({"produto": item, "quantidade": quantidade, "subtotal": subtotal})
        total += subtotal

    return itens, total
