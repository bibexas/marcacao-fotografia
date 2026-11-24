import secrets
from datetime import date, time, timedelta
from marcacao_fotografia.web.auth import auth_bp

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from marcacao_fotografia.services.pedido_service import (
    PedidoNaoEncontradoError,
    TransicaoEstadoInvalidaError,
)
from marcacao_fotografia.web.servicos import obter_servicos, fechar_conexao
from marcacao_fotografia.web.seguranca import validar_csrf, permitir_requisicao
from marcacao_fotografia import config


# Criar a aplicação Flask
def criar_app() -> Flask:
    app = Flask(__name__)
    if not config.FLASK_SECRET_KEY:
        raise RuntimeError("FLASK_SECRET_KEY não está definida. Confirme o ficheiro .env")
    app.config["SECRET_KEY"] = config.FLASK_SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = True      # o JavaScript não lê o cookie
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"     # não vai em pedidos vindos de outros sites
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    app.extensions["database_initialized"] = False
    app.teardown_appcontext(fechar_conexao)
    app.register_blueprint(auth_bp)

    @app.context_processor
    def disponibilizar_csrf_token():
        token = session.get("_csrf_token")
        if token is None:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return {"csrf_token": token}

    @app.route("/", methods=["GET"])
    def inicio():
        servicos = obter_servicos()
        return render_template(
            "inicio.html",
            tipos_evento=servicos.tipo_evento.listar_tipos_evento(),
        )

    @app.route("/submeter", methods=["POST"])
    def submeter_pedido():
        servicos = obter_servicos()
        if not permitir_requisicao("submeter", 5):
            return "Demasiadas tentativas. Tente novamente mais tarde.", 429
        validar_csrf()
        try:
            nome = request.form["nome"]
            email = request.form["email"]
            telefone = request.form["telefone"]
            id_tipo = int(request.form["id_tipo"])
            data_sessao = date.fromisoformat(request.form["data_sessao"])
            hora_inicio = time.fromisoformat(request.form["hora_inicio"])
            hora_fim = time.fromisoformat(request.form["hora_fim"])
            localizacao = request.form["localizacao"]
            observacoes = request.form.get("observacoes") or None

            try:
                cliente = servicos.cliente.obter_cliente_por_email(email)
            except ValueError:
                cliente = servicos.cliente.criar_cliente(nome, email, telefone)

            pedido = servicos.pedido.criar_pedido(
                id_cliente=cliente.id_cliente,
                id_tipo=id_tipo,
                data_sessao=data_sessao,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                localizacao=localizacao,
                observacoes=observacoes,
            )
            link_whatsapp = servicos.pedido.gerar_link_whatsapp(config.WHATSAPP_PHONE, pedido)
            flash(
                f"Pedido submetido com sucesso! Código de consulta: {pedido.codigo_consulta}",
                "sucesso",
            )
            return render_template(
                "inicio.html",
                tipos_evento=servicos.tipo_evento.listar_tipos_evento(),
                pedido_criado=pedido,
                link_whatsapp=link_whatsapp,
            )
        except ValueError as error:
            flash(f"Erro ao submeter pedido: {error}", "erro")
            return redirect(url_for("inicio"))

    @app.route("/consultar", methods=["POST"])
    def consultar_pedido():
        servicos = obter_servicos()
        if not permitir_requisicao("consultar", 10):
            return "Demasiadas tentativas. Tente novamente mais tarde.", 429
        validar_csrf()
        codigo = request.form["codigo_consulta"]
        try:
            pedido = servicos.pedido.consultar_por_codigo(codigo)
            link_whatsapp = servicos.pedido.gerar_link_whatsapp(config.WHATSAPP_PHONE, pedido)
            return render_template(
                "inicio.html",
                tipos_evento=servicos.tipo_evento.listar_tipos_evento(),
                pedido_consultado=pedido,
                link_whatsapp=link_whatsapp,
            )
        except PedidoNaoEncontradoError as error:
            flash(str(error), "erro")
            return redirect(url_for("inicio"))

    @app.route("/cancelar/<codigo>", methods=["POST"])
    def cancelar_pedido(codigo):
        servicos = obter_servicos()
        if not permitir_requisicao("cancelar", 5):
            return "Demasiadas tentativas. Tente novamente mais tarde.", 429
        validar_csrf()
        try:
            servicos.pedido.cancelar_pelo_cliente(codigo)
            flash(f"O pedido {codigo} foi cancelado com sucesso.", "sucesso")
        except (PedidoNaoEncontradoError, TransicaoEstadoInvalidaError) as error:
            flash(str(error), "erro")
        return redirect(url_for("inicio"))

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=config.FLASK_DEBUG)
