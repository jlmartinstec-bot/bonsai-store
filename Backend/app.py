
from flask import Flask, render_template
import sys
import os

# Localiza a pasta principal do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Adiciona a pasta raiz ao caminho de importação do Python
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Importa a inicialização do banco de dados
from app.database import inicializar_banco

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

# Inicializa o banco de dados
inicializar_banco()


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
