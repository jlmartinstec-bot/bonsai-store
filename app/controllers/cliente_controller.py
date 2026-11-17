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

from app.models import cliente

cliente_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

MSG_EMAIL_DUPLICADO = "Já existe um cliente cadastrado com este e-mail."


@cliente_bp.route("/")
def lista():
    try:
        itens = cliente.listar()
    except sqlite3.Error:
        flash("Não foi possível carregar os clientes.", "erro")
        itens = []
    return render_template("clientes/lista.html", clientes=itens)


@cliente_bp.route("/novo", methods=["GET", "POST"])
def novo():
    acao = url_for("clientes.novo")

    if request.method == "POST":
        dados, erros = cliente.validar(request.form)

        if not erros:
            try:
                cliente.criar(dados)
                flash("Cliente cadastrado com sucesso!", "sucesso")
                return redirect(url_for("clientes.lista"))
            except sqlite3.IntegrityError:
                erros.append(MSG_EMAIL_DUPLICADO)
            except sqlite3.Error:
                erros.append("Erro ao salvar o cliente. Tente novamente.")

        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "clientes/form.html", c=request.form, titulo="Novo cliente", acao=acao
        )

    return render_template("clientes/form.html", c={}, titulo="Novo cliente", acao=acao)


@cliente_bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
def editar(cliente_id):
    item = cliente.buscar_por_id(cliente_id)
    if item is None:
        abort(404)

    acao = url_for("clientes.editar", cliente_id=cliente_id)

    if request.method == "POST":
        dados, erros = cliente.validar(request.form)

        if not erros:
            try:
                cliente.atualizar(cliente_id, dados)
                flash("Cliente atualizado com sucesso!", "sucesso")
                return redirect(url_for("clientes.lista"))
            except sqlite3.IntegrityError:
                erros.append(MSG_EMAIL_DUPLICADO)
            except sqlite3.Error:
                erros.append("Erro ao salvar o cliente. Tente novamente.")

        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "clientes/form.html", c=request.form, titulo="Editar cliente", acao=acao
        )

    return render_template("clientes/form.html", c=item, titulo="Editar cliente", acao=acao)


@cliente_bp.route("/<int:cliente_id>/excluir", methods=["POST"])
def excluir(cliente_id):
    try:
        removidos = cliente.excluir(cliente_id)
        if removidos:
            flash("Cliente excluído.", "sucesso")
        else:
            flash("Cliente não encontrado.", "erro")
    except sqlite3.IntegrityError:
        flash("Este cliente já tem pedidos e não pode ser excluído.", "erro")
    except sqlite3.Error:
        flash("Erro ao excluir o cliente.", "erro")

    return redirect(url_for("clientes.lista"))
