from enum import Enum

class EstadoPedido(str, Enum):
    PENDENTE = "Pendente"
    CONFIRMADA = "Confirmada"
    REALIZADA = "Realizada"
    EM_TRATAMENTO = "Em Tratamento"
    ENTREGUE = "Entregue"
    CANCELADA = "Cancelada"