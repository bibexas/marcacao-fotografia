import os
import secrets
from datetime import date, time

from flask import Flask, current_app, flash, g, redirect, render_template, request, url_for

from marcacao_fotografia.database import iniciar_bd, obter_conexao
from marcacao_fotografia.repositories.cliente_repository import ClienteRepository
from marcacao_fotografia.repositories.pedido_repository import PedidoRepository
from marcacao_fotografia.repositories.tipo_evento_repository import TipoEventoRepository
from marcacao_fotografia.services.cliente_service import ClienteService
from marcacao_fotografia.services.pedido_service import (
    PedidoNaoEncontradoError,
    PedidoService,
    TransicaoEstadoInvalidaError,
)
from marcacao_fotografia.services.tipo_evento_service import TipoEventoService


TELEFONE_EQUIPA = "+351 912 345 678"


def _obter_servicos():
    if "servicos" not in g:
        if not current_app.extensions.get("database_initialized"):
            iniciar_bd()
            current_app.extensions["database_initialized"] = True

        conexao = obter_conexao()
        cliente_repo = ClienteRepository(conexao)
        tipo_evento_repo = TipoEventoRepository(conexao)
        pedido_repo = PedidoRepository(conexao)
        g.conexao = conexao
        g.servicos = (
            ClienteService(cliente_repo),
            TipoEventoService(tipo_evento_repo),
            PedidoService(pedido_repo, cliente_repo, tipo_evento_repo),
            pedido_repo,
        )
    return g.servicos


def _fechar_conexao(_exception=None):
    conexao = g.pop("conexao", None)
    if conexao is not None:
        conexao.close()


def criar_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
    app.extensions["database_initialized"] = False
    app.teardown_appcontext(_fechar_conexao)

    @app.route("/", methods=["GET"])
    def inicio():
        _, tipo_evento_service, pedido_service, pedido_repo = _obter_servicos()
        return render_template(
            "inicio.html",
            tipos_evento=tipo_evento_service.listar_tipos_evento(),
            pedidos=pedido_repo.listar_todos(),
        )

    @app.route("/submeter", methods=["POST"])
    def submeter_pedido():
        cliente_service, tipo_evento_service, pedido_service, _ = _obter_servicos()
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
                cliente = cliente_service.obter_cliente_por_email(email)
            except ValueError:
                cliente = cliente_service.criar_cliente(nome, email, telefone)

            pedido = pedido_service.criar_pedido(
                id_cliente=cliente.id_cliente,
                id_tipo=id_tipo,
                data_sessao=data_sessao,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                localizacao=localizacao,
                observacoes=observacoes,
            )
            link_whatsapp = pedido_service.gerar_link_whatsapp(TELEFONE_EQUIPA, pedido)
            flash(
                f"Pedido submetido com sucesso! Código de consulta: {pedido.codigo_consulta}",
                "sucesso",
            )
            return render_template(
                "inicio.html",
                tipos_evento=tipo_evento_service.listar_tipos_evento(),
                pedidos=pedido_service.listar_pedidos(),
                pedido_criado=pedido,
                link_whatsapp=link_whatsapp,
            )
        except ValueError as error:
            flash(f"Erro ao submeter pedido: {error}", "erro")
            return redirect(url_for("inicio"))

    @app.route("/consultar", methods=["POST"])
    def consultar_pedido():
        _, tipo_evento_service, pedido_service, _ = _obter_servicos()
        codigo = request.form["codigo_consulta"]
        try:
            pedido = pedido_service.consultar_por_codigo(codigo)
            link_whatsapp = pedido_service.gerar_link_whatsapp(TELEFONE_EQUIPA, pedido)
            return render_template(
                "inicio.html",
                tipos_evento=tipo_evento_service.listar_tipos_evento(),
                pedidos=pedido_service.listar_pedidos(),
                pedido_consultado=pedido,
                link_whatsapp=link_whatsapp,
            )
        except PedidoNaoEncontradoError as error:
            flash(str(error), "erro")
            return redirect(url_for("inicio"))

    @app.route("/cancelar/<codigo>", methods=["POST"])
    def cancelar_pedido(codigo):
        _, _, pedido_service, _ = _obter_servicos()
        try:
            pedido_service.cancelar_pelo_cliente(codigo)
            flash(f"O pedido {codigo} foi cancelado com sucesso.", "sucesso")
        except (PedidoNaoEncontradoError, TransicaoEstadoInvalidaError) as error:
            flash(str(error), "erro")
        return redirect(url_for("inicio"))

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "").lower() == "true")
