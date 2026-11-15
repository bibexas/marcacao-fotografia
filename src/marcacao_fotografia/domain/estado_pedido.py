from enum import Enum

# Definição dos estados possíveis para um pedido
class EstadoPedido(str, Enum):
    PENDENTE = "Pendente"
    CONFIRMADA = "Confirmada"
    REALIZADA = "Realizada"
    EM_TRATAMENTO = "Em Tratamento"
    ENTREGUE = "Entregue"
    CANCELADA = "Cancelada"