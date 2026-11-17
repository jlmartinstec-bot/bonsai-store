import sqlite3

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.models import carrinho, cliente, pedido

carrinho_bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")


@carrinho_bp.route("/")
def ver():
    try:
        itens, total = carrinho.itens_detalhados(session.get("carrinho", {}))
        clientes = cliente.listar()
    except sqlite3.Error:
        flash("Não foi possível carregar o carrinho.", "erro")
        itens, total, clientes = [], 0.0, []
    return render_template(
        "carrinho/ver.html", itens=itens, total=total, clientes=clientes
    )


@carrinho_bp.route("/adicionar/<int:produto_id>", methods=["POST"])
def adicionar(produto_id):
    atual = dict(session.get("carrinho", {}))
    try:
        carrinho.adicionar(atual, produto_id)
        session["carrinho"] = atual
        flash("Produto adicionado ao carrinho.", "sucesso")
    except ValueError as erro:
        flash(str(erro), "erro")
    except sqlite3.Error:
        flash("Erro ao adicionar o produto. Tente novamente.", "erro")
    return redirect(url_for("home.home"))


@carrinho_bp.route("/remover/<int:produto_id>", methods=["POST"])
def remover(produto_id):
    atual = dict(session.get("carrinho", {}))
    carrinho.remover(atual, produto_id)
    session["carrinho"] = atual
    flash("Produto removido do carrinho.", "sucesso")
    return redirect(url_for("carrinho.ver"))


@carrinho_bp.route("/finalizar", methods=["POST"])
def finalizar():
    atual = session.get("carrinho", {})
    if not atual:
        flash("Seu carrinho está vazio.", "erro")
        return redirect(url_for("carrinho.ver"))

    try:
        cliente_id = int(request.form.get("cliente_id", ""))
    except ValueError:
        flash("Escolha o cliente do pedido.", "erro")
        return redirect(url_for("carrinho.ver"))

    itens = {int(chave): quantidade for chave, quantidade in atual.items()}

    try:
        pedido_id = pedido.criar_pedido(cliente_id, itens)
    except ValueError as erro:  # inclui EstoqueInsuficiente
        flash(str(erro), "erro")
        return redirect(url_for("carrinho.ver"))
    except sqlite3.Error:
        flash("Erro ao registrar o pedido. Tente novamente.", "erro")
        return redirect(url_for("carrinho.ver"))

    session.pop("carrinho", None)
    flash("Pedido realizado com sucesso!", "sucesso")
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido_id))
