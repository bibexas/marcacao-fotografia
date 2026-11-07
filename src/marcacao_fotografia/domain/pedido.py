from dataclasses import dataclass
from datetime import date, time, datetime
from .estado_pedido import EstadoPedido

class DadosPedidoInvalidos(ValueError):
    pass

class OperacaoPedidoInvalida(ValueError):
    pass

@dataclass(frozen=True)
class Pedido:
    id_pedido: int | None
    codigo_consulta: str
    data_sessao: date
    hora_inicio: time
    hora_fim: time
    localizacao: str
    duracao: int = 0
    estado: EstadoPedido
    observacoes: str | None
    id_cliente: int
    id_tipo: int

    def __post_init__(self):

        if self.hora_fim <= self.hora_inicio:
            raise DadosPedidoInvalidos("A hora de fim deve ser posterior à hora de início.")

        if len(self.codigo_consulta) != 8:
            raise DadosPedidoInvalidos("O código de consulta deve ter 8 caracteres.")

        localizacao_limpa = self.localizacao.strip()
        if not localizacao_limpa:
            raise DadosPedidoInvalidos("A localização é obrigatória.")

        dt_inicio = datetime.combine(self.data_sessao, self.hora_inicio)
        dt_fim = datetime.combine(self.data_sessao, self.hora_fim)
        minutos = int((dt_fim - dt_inicio).total_seconds() / 60)

        object.__setattr__(self, "duracao", minutos)
        object.__setattr__(self, "localizacao", localizacao_limpa)

    def cliente_cancelar(self) -> bool:
        return self.estado in {EstadoPedido.PENDENTE}

    def equipa_cancelar(self) -> bool:
        return self.estado in {EstadoPedido.PENDENTE, EstadoPedido.CONFIRMADA}