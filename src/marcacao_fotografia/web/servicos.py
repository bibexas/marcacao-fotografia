from types import SimpleNamespace
from flask import current_app, g
from marcacao_fotografia.database import iniciar_bd, obter_conexao
from marcacao_fotografia.repositories.administrador_repository import AdministradorRepository
from marcacao_fotografia.repositories.cliente_repository import ClienteRepository
from marcacao_fotografia.repositories.pedido_repository import PedidoRepository
from marcacao_fotografia.repositories.tipo_evento_repository import TipoEventoRepository
from marcacao_fotografia.services.auth_service import AuthService
from marcacao_fotografia.services.cliente_service import ClienteService
from marcacao_fotografia.services.pedido_service import PedidoService
from marcacao_fotografia.services.tipo_evento_service import TipoEventoService

def obter_servicos():
    if "servicos" not in g:
        if not current_app.extensions.get("database_initialized"):
            iniciar_bd()
            current_app.extensions["database_initialized"] = True

        conexao = obter_conexao()
        cliente_repo = ClienteRepository(conexao)
        tipo_evento_repo = TipoEventoRepository(conexao)
        pedido_repo = PedidoRepository(conexao)
        g.conexao = conexao
        g.servicos = SimpleNamespace(
            cliente=ClienteService(cliente_repo),
            tipo_evento=TipoEventoService(tipo_evento_repo),
            pedido=PedidoService(pedido_repo, cliente_repo, tipo_evento_repo),
            auth=AuthService(AdministradorRepository(conexao)),
        )
    return g.servicos

# Fechar a conexão à base de dados ao terminar o contexto da aplicação
def fechar_conexao(_exception=None):
    conexao = g.pop("conexao", None)
    if conexao is not None:
        conexao.close()