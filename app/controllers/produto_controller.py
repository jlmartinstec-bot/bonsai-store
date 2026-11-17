import os
import sqlite3
import uuid

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import produto

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")


def _erro_imagem(arquivo):
    """Confere o arquivo enviado. Devolve a mensagem de erro ou None."""
    if arquivo is None or arquivo.filename == "":
        return None
    if not produto.extensao_permitida(arquivo.filename):
        return "A imagem deve ser PNG, JPG, GIF ou WEBP."
    return None


def _salvar_imagem(arquivo):
    """Salva a imagem na pasta de uploads e devolve o nome do arquivo."""
    if arquivo is None or arquivo.filename == "":
        return None
    extensao = arquivo.filename.rsplit(".", 1)[1].lower()
    nome = f"{uuid.uuid4().hex}.{extensao}"
    arquivo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], nome))
    return nome


def _remover_imagem(nome):
    """Apaga o arquivo de imagem (se existir)."""
    if not nome:
        return
    try:
        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], nome))
    except OSError:
        pass


@produto_bp.route("/")
def lista():
    try:
        itens = produto.listar()
    except sqlite3.Error:
        flash("Não foi possível carregar os produtos.", "erro")
        itens = []
    return render_template("produtos/lista.html", produtos=itens)


@produto_bp.route("/novo", methods=["GET", "POST"])
def novo():
    acao = url_for("produtos.novo")

    if request.method == "POST":
        arquivo = request.files.get("imagem")
        dados, erros = produto.validar(request.form)
        erro_imagem = _erro_imagem(arquivo)
        if erro_imagem:
            erros.append(erro_imagem)

        if not erros:
            nome_imagem = None
            try:
                nome_imagem = _salvar_imagem(arquivo)
                dados["imagem"] = nome_imagem
                produto.criar(dados)
                flash("Produto cadastrado com sucesso!", "sucesso")
                return redirect(url_for("produtos.lista"))
            except (sqlite3.Error, OSError):
                _remover_imagem(nome_imagem)
                erros.append("Erro ao salvar o produto. Tente novamente.")

        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "produtos/form.html",
            p=request.form,
            imagem_atual=None,
            titulo="Novo produto",
            acao=acao,
        )

    return render_template(
        "produtos/form.html", p={}, imagem_atual=None, titulo="Novo produto", acao=acao
    )


@produto_bp.route("/<int:produto_id>/editar", methods=["GET", "POST"])
def editar(produto_id):
    item = produto.buscar_por_id(produto_id)
    if item is None:
        abort(404)

    acao = url_for("produtos.editar", produto_id=produto_id)

    if request.method == "POST":
        arquivo = request.files.get("imagem")
        dados, erros = produto.validar(request.form)
        erro_imagem = _erro_imagem(arquivo)
        if erro_imagem:
            erros.append(erro_imagem)

        if not erros:
            nome_imagem = None
            try:
                nome_imagem = _salvar_imagem(arquivo)
                dados["imagem"] = nome_imagem  # None mantém a imagem atual
                produto.atualizar(produto_id, dados)
                if nome_imagem:
                    _remover_imagem(item["imagem"])
                flash("Produto atualizado com sucesso!", "sucesso")
                return redirect(url_for("produtos.lista"))
            except (sqlite3.Error, OSError):
                _remover_imagem(nome_imagem)
                erros.append("Erro ao salvar o produto. Tente novamente.")

        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "produtos/form.html",
            p=request.form,
            imagem_atual=item["imagem"],
            titulo="Editar produto",
            acao=acao,
        )

    return render_template(
        "produtos/form.html",
        p=item,
        imagem_atual=item["imagem"],
        titulo="Editar produto",
        acao=acao,
    )


@produto_bp.route("/<int:produto_id>/excluir", methods=["POST"])
def excluir(produto_id):
    try:
        item = produto.buscar_por_id(produto_id)
        removidos = produto.excluir(produto_id)
        if removidos:
            if item is not None:
                _remover_imagem(item["imagem"])
            flash("Produto excluído.", "sucesso")
        else:
            flash("Produto não encontrado.", "erro")
    except sqlite3.IntegrityError:
        flash("Este produto já está em pedidos e não pode ser excluído.", "erro")
    except sqlite3.Error:
        flash("Erro ao excluir o produto.", "erro")

    return redirect(url_for("produtos.lista"))
