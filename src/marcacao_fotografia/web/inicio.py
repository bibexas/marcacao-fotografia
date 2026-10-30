from flask import Blueprint, render_template

bp = Blueprint("inicio", __name__)

@bp.route("/")
def pagina_inicial():
    return render_template("index.html")