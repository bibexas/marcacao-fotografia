from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from marcacao_fotografia.web.servicos import obter_servicos
from marcacao_fotografia.services.auth_service import CredenciaisInvalidasError
from marcacao_fotografia.web.seguranca import validar_csrf, permitir_requisicao

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        servicos = obter_servicos()
        if not permitir_requisicao("login", 5):
            return "Demasiadas tentativas. Tente novamente mais tarde.", 429

        validar_csrf()
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        try:
            administrador = servicos.auth.login(username, password)
        except CredenciaisInvalidasError as erro:
            flash(str(erro), "erro")
        else:
            session.clear()
            session["id_admin"] = administrador.id_admin
            session.permanent = True
            return redirect(url_for("admin.painel"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    validar_csrf()
    session.clear()
    flash("Sessão encerrada com sucesso.", "sucesso")
    return redirect(url_for("auth.login"))
