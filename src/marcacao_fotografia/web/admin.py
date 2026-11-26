from flask import Blueprint, flash, redirect, render_template, request, url_for

from marcacao_fotografia.domain.estado_pedido import EstadoPedido
from marcacao_fotografia.web.seguranca import validar_csrf
from marcacao_fotografia.web.decorators import login_required
from marcacao_fotografia.web.servicos import obter_servicos

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

PROXIMO_ESTADO = {
    "Pendente": "Confirmada",
    "Confirmada": "Realizada",
    "Realizada": "Em Tratamento",
    "Em Tratamento": "Entregue",
}
ROTULOS_ACAO = {
    "Confirmada": "Confirmar",
    "Realizada": "Marcar como realizada",
    "Em Tratamento": "Passar a em tratamento",
    "Entregue": "Marcar como entregue",
}


@admin_bp.route("/")
@login_required
def painel():
    servicos = obter_servicos()
    pedidos = servicos.pedido.listar_pedidos_com_detalhes()
    return render_template(
        "admin/dashboard.html",
        pedidos=pedidos,
        proximos=PROXIMO_ESTADO,
        rotulos=ROTULOS_ACAO,
    )


@admin_bp.route("/pedidos/<int:id_pedido>/estado", methods=["POST"])
@login_required
def alterar_estado_pedido(id_pedido):
    validar_csrf()
    valor = request.form.get("estado", "")
    try:
        novo_estado = EstadoPedido(valor)
        servicos = obter_servicos()
        servicos.pedido.alterar_estado_equipa(id_pedido, novo_estado)
        flash("Estado do pedido atualizado com sucesso.", "sucesso")
    except ValueError as erro:
        flash(str(erro), "erro")
    return redirect(url_for("admin.painel"))
