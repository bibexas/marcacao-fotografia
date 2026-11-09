from datetime import date, time
import unittest
from unittest.mock import MagicMock

from marcacao_fotografia.repositories.cliente_repository import ClienteRepository
from marcacao_fotografia.repositories.pedido_repository import PedidoRepository
from marcacao_fotografia.repositories.tipo_evento_repository import TipoEventoRepository
from marcacao_fotografia.domain.cliente import Cliente
from marcacao_fotografia.domain.pedido import Pedido
from marcacao_fotografia.domain.estado_pedido import EstadoPedido

class TestRepositories(unittest.TestCase):
    def setUp(self):
        self.conexao_mock = MagicMock()
        self.cursor_mock = MagicMock()
        self.conexao_mock.cursor.return_value.__enter__.return_value = self.cursor_mock
        self.cliente_repo = ClienteRepository(self.conexao_mock)
        self.pedido_repo = PedidoRepository(self.conexao_mock)
        self.tipo_evento_repo = TipoEventoRepository(self.conexao_mock)

    def test_guardar_cliente(self):
        self.cursor_mock.fetchone.return_value = {"id_cliente": 1}
        cliente_in = Cliente(id_cliente=None, nome="João", email="joaosilva@gmail.com", telefone="912345678")
        cliente_out = self.cliente_repo.guardar_cliente(cliente_in)
        self.assertEqual(cliente_out.id_cliente, 1)
        self.assertEqual(cliente_out.nome, "João")
        self.assertEqual(cliente_out.email, "joaosilva@gmail.com")
        self.assertEqual(cliente_out.telefone, "912345678")

    def test_procurar_email(self):
        self.cursor_mock.fetchone.return_value = {"id_cliente": 1, "nome": "João", "email": "joaosilva@gmail.com", "telefone": "912345678"}
        cliente = self.cliente_repo.procurar_email("joaosilva@gmail.com")
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nome, "João")
        self.assertEqual(cliente.email, "joaosilva@gmail.com")

    def test_procurar_id(self):
        self.cursor_mock.fetchone.return_value = {"id_cliente": 1, "nome": "João", "email": "joaosilva@gmail.com", "telefone": "912345678"}
        cliente = self.cliente_repo.procurar_id(1)
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.id_cliente, 1)

    def test_guardar_pedido(self):
        self.cursor_mock.fetchone.return_value = {"id_pedido": 10}
        pedido_in = Pedido(
            id_pedido=None,
            codigo_consulta="ABC12345",
            data_sessao=date(2024, 6, 15),
            hora_inicio=time(14, 30),
            hora_fim=time(15, 30),
            localizacao="Praia da Rocha",
            estado=EstadoPedido.PENDENTE,
            observacoes="Fotografia de casamento",
            id_cliente=1,
            id_tipo=1
        )

        pedido_out = self.pedido_repo.guardar_pedido(pedido_in)
        self.assertEqual(pedido_out.id_pedido, 10)
        self.assertEqual(pedido_out.codigo_consulta, "ABC12345")
        self.assertEqual(pedido_out.id_cliente, 1)

    def test_procurar_codigo(self):
        self.cursor_mock.fetchone.return_value = {
            "id_pedido": 1,
            "codigo_consulta": "ABC12345",
            "data_sessao": date(2024, 6, 15),
            "hora_inicio": time(14, 30),
            "hora_fim": time(15, 30),
            "localizacao": "Praia da Rocha",
            "duracao": 60,
            "estado": "Pendente",
            "observacoes": "Fotografia de casamento",
            "id_cliente": 1,
            "id_tipo": 1
        }
        pedido = self.pedido_repo.procurar_codigo("ABC12345")
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.codigo_consulta, "ABC12345")

    def test_listar_todos(self):
        self.cursor_mock.fetchall.return_value = [{
            "id_pedido": 1,
            "codigo_consulta": "ABC12345",
            "data_sessao": date(2024, 6, 15),
            "hora_inicio": time(14, 30),
            "hora_fim": time(15, 30),
            "localizacao": "Praia da Rocha",
            "duracao": 60,
            "estado": "Pendente",
            "observacoes": "Fotografia de casamento",
            "id_cliente": 1,
            "id_tipo": 1
        }]
        pedidos = self.pedido_repo.listar_todos()
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(pedidos[0].codigo_consulta, "ABC12345")

    def test_consultar_sobreposicoes(self):
        self.cursor_mock.fetchall.return_value = []
        sobreposicoes = self.pedido_repo.consultar_sobreposicoes(
            date(2024, 6, 15), time(14, 0), time(15, 0)
        )
        self.assertIsInstance(sobreposicoes, list)

    def test_atualizar_estado(self):
        self.pedido_repo.atualizar_estado(1, EstadoPedido.CONFIRMADA)
        self.cursor_mock.execute.assert_called_once()

    def test_listar_tipos_evento(self):
        self.cursor_mock.fetchall.return_value = [
            {"id_tipo": 1, "tipo": "Casamento"},
            {"id_tipo": 2, "tipo": "Batizado"}
        ]
        tipos = self.tipo_evento_repo.listar_tipos_evento()
        self.assertEqual(len(tipos), 2)
        self.assertEqual(tipos[0].tipo, "Casamento")

    def test_procurar_por_id(self):
        self.cursor_mock.fetchone.return_value = {"id_tipo": 1, "tipo": "Casamento"}
        tipo = self.tipo_evento_repo.procurar_por_id(1)

        self.assertIsNotNone(tipo)
        self.assertEqual(tipo.id_tipo, 1)
        self.assertEqual(tipo.tipo, "Casamento")

if __name__ == "__main__":
    unittest.main()