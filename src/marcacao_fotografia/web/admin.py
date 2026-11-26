from flask import Blueprint, render_template

from marcacao_fotografia.web.decorators import login_required
from marcacao_fotografia.web.servicos import obter_servicos

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@login_required
def painel():
    servicos = obter_servicos()
    pedidos = servicos.pedido.listar_pedidos_com_detalhes()
    return render_template("admin/dashboard.html", pedidos=pedidos)