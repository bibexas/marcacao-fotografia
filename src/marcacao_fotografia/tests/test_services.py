from datetime import date, time
import unittest
from unittest.mock import Mock

from marcacao_fotografia.domain.estado_pedido import EstadoPedido
from marcacao_fotografia.domain.pedido import Pedido
from marcacao_fotografia.repositories.pedido_repository import PedidoRepository
from marcacao_fotografia.services.pedido_service import PedidoService


class TestPedidoService(unittest.TestCase):
    def setUp(self):
        self.pedido_repo = Mock(spec=PedidoRepository)
        self.cliente_repo = Mock()
        self.tipo_evento_repo = Mock()
        self.cliente_repo.procurar_id.return_value = object()
        self.tipo_evento_repo.procurar_por_id.return_value = object()
        self.pedido_repo.existe_sobreposicao.return_value = False
        self.pedido_repo.procurar_codigo.return_value = None
        self.pedido_repo.guardar_pedido.side_effect = lambda pedido: pedido
        self.pedido_repo.atualizar.side_effect = lambda pedido: pedido
        self.service = PedidoService(
            self.pedido_repo,
            self.cliente_repo,
            self.tipo_evento_repo,
        )

    def test_criar_pedido_usa_contrato_do_repositorio(self):
        pedido = self.service.criar_pedido(
            1,
            1,
            date(2026, 1, 1),
            time(10),
            time(11),
            "Local",
        )

        self.assertEqual(pedido.estado, EstadoPedido.PENDENTE)
        self.assertEqual(pedido.duracao, 60)
        self.pedido_repo.guardar_pedido.assert_called_once()

    def test_cancelar_pedido_preserva_imutabilidade_do_pedido(self):
        pedido = Pedido(
            1,
            "ABC12345",
            date(2026, 1, 1),
            time(10),
            time(11),
            "Local",
            EstadoPedido.PENDENTE,
            None,
            1,
            1,
        )
        self.pedido_repo.procurar_codigo.return_value = pedido

        cancelado = self.service.cancelar_pelo_cliente("abc12345")

        self.assertEqual(cancelado.estado, EstadoPedido.CANCELADA)
        self.assertEqual(pedido.estado, EstadoPedido.PENDENTE)
