from datetime import date, time
import uuid
from urllib.parse import quote

from marcacao_fotografia.domain.pedido import Pedido, EstadoPedido
from marcacao_fotografia.repositories.pedido_repository import PedidoRepository
from marcacao_fotografia.repositories.cliente_repository import ClienteRepository
from marcacao_fotografia.repositories.tipo_evento_repository import TipoEventoRepository


class PedidoNaoEncontradoError(ValueError):
    pass


class HorarioIndisponivelError(ValueError):
    pass


class TransicaoEstadoInvalidaError(ValueError):
    pass


class PedidoService:
    ORDEM_ESTADOS = [
        EstadoPedido.PENDENTE,
        EstadoPedido.CONFIRMADA,
        EstadoPedido.REALIZADA,
        EstadoPedido.EM_TRATAMENTO,
        EstadoPedido.ENTREGUE,
    ]

    def __init__(
        self,
        pedido_repo: PedidoRepository,
        cliente_repo: ClienteRepository,
        tipo_evento_repo: TipoEventoRepository,
    ):
        self.pedido_repo = pedido_repo
        self.cliente_repo = cliente_repo
        self.tipo_evento_repo = tipo_evento_repo

    def _gerar_codigo_unico(self) -> str:
        while True:
            codigo = uuid.uuid4().hex[:8].upper()
            if not self.pedido_repo.procurar_por_codigo(codigo):
                return codigo

    def criar_pedido(
        self,
        id_cliente: int,
        id_tipo: int,
        data_sessao: date,
        hora_inicio: time,
        hora_fim: time,
        localizacao: str,
        observacoes: str | None = None,
    ) -> Pedido:
        if not self.cliente_repo.procurar_id(id_cliente):
            raise ValueError(f"Cliente com ID {id_cliente} não existe.")

        if not self.tipo_evento_repo.procurar_id(id_tipo):
            raise ValueError(f"Tipo de evento com ID {id_tipo} não existe.")

        if self.pedido_repo.existe_sobreposicao(data_sessao, hora_inicio, hora_fim):
            raise HorarioIndisponivelError("O horário selecionado já se encontra ocupado.")

        codigo = self._gerar_codigo_unico()

        novo_pedido = Pedido(
            id_pedido=None,
            codigo_consulta=codigo,
            data_sessao=data_sessao,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            localizacao=localizacao,
            estado=EstadoPedido.PENDENTE,
            observacoes=observacoes,
            id_cliente=id_cliente,
            id_tipo=id_tipo,
        )

        return self.pedido_repo.guardar(novo_pedido)

    def consultar_por_codigo(self, codigo_consulta: str) -> Pedido:
        pedido = self.pedido_repo.procurar_por_codigo(codigo_consulta.strip().upper())
        if not pedido:
            raise PedidoNaoEncontradoError(f"Pedido com código '{codigo_consulta}' não encontrado.")
        return pedido

    def listar_pedidos(self) -> list[Pedido]:
        return self.pedido_repo.listar_todos()

    def listar_horarios_indisponiveis(self, data_sessao: date) -> list[tuple[time, time]]:
        pedidos_confirmados = self.pedido_repo.listar_confirmados_por_data(data_sessao)
        return [(p.hora_inicio, p.hora_fim) for p in pedidos_confirmados]

    def cancelar_pelo_cliente(self, codigo_consulta: str) -> Pedido:
        pedido = self.consultar_por_codigo(codigo_consulta)

        if pedido.estado != EstadoPedido.PENDENTE:
            raise TransicaoEstadoInvalidaError(
                "Não é possível cancelar online porque o pedido já foi confirmado ou processado. "
                "Por favor, contacte a equipa diretamente."
            )

        pedido.estado = EstadoPedido.CANCELADA
        return self.pedido_repo.atualizar(pedido)

    def alterar_estado_equipa(self, id_pedido: int, novo_estado: EstadoPedido) -> Pedido:
        pedido = self.pedido_repo.procurar_id(id_pedido)
        if not pedido:
            raise PedidoNaoEncontradoError(f"Pedido com ID {id_pedido} não encontrado.")

        if novo_estado == EstadoPedido.CANCELADA:
            if pedido.estado not in (EstadoPedido.PENDENTE, EstadoPedido.CONFIRMADA):
                raise TransicaoEstadoInvalidaError(
                    f"Não é possível cancelar um pedido no estado '{pedido.estado.value}'."
                )
            pedido.estado = EstadoPedido.CANCELADA
            return self.pedido_repo.atualizar(pedido)

        if pedido.estado not in self.ORDEM_ESTADOS or novo_estado not in self.ORDEM_ESTADOS:
            raise TransicaoEstadoInvalidaError(
                f"Transição inválida de '{pedido.estado.value}' para '{novo_estado.value}'."
            )

        idx_atual = self.ORDEM_ESTADOS.index(pedido.estado)
        idx_novo = self.ORDEM_ESTADOS.index(novo_estado)

        if idx_novo != idx_atual + 1:
            raise TransicaoEstadoInvalidaError(
                f"O estado deve seguir a ordem sequencial. Não pode passar de '{pedido.estado.value}' para '{novo_estado.value}'."
            )

        if novo_estado == EstadoPedido.CONFIRMADA:
            if self.pedido_repo.existe_sobreposicao(
                pedido.data_sessao, pedido.hora_inicio, pedido.hora_fim, ignorar_id=pedido.id_pedido
            ):
                raise HorarioIndisponivelError(
                    "Não é possível confirmar: já existe outro pedido confirmado neste horário."
                )

        pedido.estado = novo_estado
        return self.pedido_repo.atualizar(pedido)

    def gerar_link_whatsapp(self, telefone_destino: str, pedido: Pedido) -> str:
        telefone_limpo = "".join(filter(str.isdigit, telefone_destino))
        if not telefone_limpo.startswith("351") and len(telefone_limpo) == 9:
            telefone_limpo = f"351{telefone_limpo}"

        mensagem = (
            f"Olá! Gostaria de falar sobre o pedido de fotografia com o código {pedido.codigo_consulta} "
            f"para o dia {pedido.data_sessao.strftime('%d/%m/%Y')} "
            f"({pedido.hora_inicio.strftime('%H:%M')} - {pedido.hora_fim.strftime('%H:%M')}) "
            f"em {pedido.localizacao}."
        )
        return f"https://wa.me/{telefone_limpo}?text={quote(mensagem)}"