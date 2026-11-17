import sqlite3

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import pedido

pedido_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@pedido_bp.route("/")
def lista():
    try:
        itens = pedido.listar()
    except sqlite3.Error:
        flash("Não foi possível carregar os pedidos.", "erro")
        itens = []
    return render_template("pedidos/lista.html", pedidos=itens)


@pedido_bp.route("/<int:pedido_id>")
def detalhe(pedido_id):
    registro, itens, total = pedido.buscar(pedido_id)
    if registro is None:
        abort(404)
    return render_template(
        "pedidos/detalhe.html",
        pedido=registro,
        itens=itens,
        total=total,
        status_validos=pedido.STATUS_VALIDOS,
    )


@pedido_bp.route("/<int:pedido_id>/status", methods=["POST"])
def status(pedido_id):
    try:
        alterados = pedido.atualizar_status(pedido_id, request.form.get("status", ""))
        if alterados:
            flash("Status do pedido atualizado.", "sucesso")
        else:
            flash("Pedido não encontrado.", "erro")
    except ValueError as erro:
        flash(str(erro), "erro")
    except sqlite3.Error:
        flash("Erro ao atualizar o pedido.", "erro")

    return redirect(url_for("pedidos.detalhe", pedido_id=pedido_id))
