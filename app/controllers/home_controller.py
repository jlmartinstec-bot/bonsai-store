import sqlite3

from flask import Blueprint, flash, render_template

from app.models import produto

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    try:
        itens = produto.listar()
    except sqlite3.Error:
        flash("Não foi possível carregar os produtos.", "erro")
        itens = []
    return render_template("home.html", produtos=itens)
