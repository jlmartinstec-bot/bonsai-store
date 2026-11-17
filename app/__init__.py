import os

from flask import Flask, render_template, session

from app import database


def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "bonsai-store-dev")
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024  # fotos de até 3 MB

    if config:
        app.config.update(config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Cria as tabelas ao iniciar a aplicação
    database.inicializar_banco()

    # Formata valores em reais: 89.9 -> R$ 89,90
    @app.template_filter("brl")
    def formatar_reais(valor):
        texto = f"{valor:,.2f}"
        return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

    # Quantidade de itens no carrinho, disponível em todas as telas
    @app.context_processor
    def dados_globais():
        return {"qtd_carrinho": sum(session.get("carrinho", {}).values())}

    from app.controllers.carrinho_controller import carrinho_bp
    from app.controllers.cliente_controller import cliente_bp
    from app.controllers.home_controller import home_bp
    from app.controllers.pedido_controller import pedido_bp
    from app.controllers.produto_controller import produto_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(carrinho_bp)
    app.register_blueprint(pedido_bp)

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return (
            render_template("erro.html", codigo=404, mensagem="Página não encontrada."),
            404,
        )

    @app.errorhandler(413)
    def arquivo_grande_demais(erro):
        return (
            render_template(
                "erro.html",
                codigo=413,
                mensagem="A imagem é grande demais. O limite é de 3 MB.",
            ),
            413,
        )

    @app.errorhandler(500)
    def erro_interno(erro):
        return (
            render_template(
                "erro.html",
                codigo=500,
                mensagem="Ocorreu um erro inesperado. Tente novamente.",
            ),
            500,
        )

    return app
