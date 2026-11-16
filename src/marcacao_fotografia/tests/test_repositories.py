from datetime import date, time
import unittest
from unittest.mock import MagicMock

from marcacao_fotografia.repositories.cliente_repository import ClienteRepository
from marcacao_fotografia.repositories.pedido_repository import PedidoRepository
from marcacao_fotografia.repositories.tipo_evento_repository import TipoEventoRepository
from marcacao_fotografia.repositories.administrador_repository import AdministradorRepository
from marcacao_fotografia.domain.cliente import Cliente
from marcacao_fotografia.domain.pedido import Pedido
from marcacao_fotografia.domain.estado_pedido import EstadoPedido
from marcacao_fotografia.domain.administrador import Administrador

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

    def test_guardar_cliente_faz_rollback_se_falhar(self):
        conexao = MagicMock()
        cursor = conexao.cursor.return_value.__enter__.return_value
        cursor.execute.side_effect = Exception("Erro SQL")
        repositorio = ClienteRepository(conexao)
        cliente = Cliente(None, "Ana", "ana@exemplo.pt", "912345678")

        with self.assertRaisesRegex(Exception, "Erro SQL"):
            repositorio.guardar_cliente(cliente)

        conexao.rollback.assert_called_once()
        conexao.commit.assert_not_called()

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

    def test_procurar_username(self):
        self.cursor_mock.fetchone.return_value = {"id_admin": 1, "username": "admin", "password_hash": "hashed_password"}
        admin = AdministradorRepository(self.conexao_mock).procurar_por_username("admin")

        self.assertIsNotNone(admin)
        self.assertEqual(admin.id_admin, 1)
        self.assertEqual(admin.username, "admin")
        self.assertEqual(admin.password_hash, "hashed_password")

    def test_procurar_por_username_inexistente(self):
        self.cursor_mock.fetchone.return_value = None
        admin = AdministradorRepository(self.conexao_mock).procurar_por_username("naoexiste")

        self.assertIsNone(admin)

    def test_guardar_administrador(self):
        self.cursor_mock.fetchone.return_value = {"id_admin": 1}
        admin_in = Administrador(id_admin=None, username="admin", password_hash="hashed_password")
        admin_out = AdministradorRepository(self.conexao_mock).guardar_administrador(admin_in)

        self.assertEqual(admin_out.id_admin, 1)
        self.assertEqual(admin_out.username, "admin")
        self.assertEqual(admin_out.password_hash, "hashed_password")
        self.conexao_mock.commit.assert_called_once()
        self.conexao_mock.rollback.assert_not_called()

    def test_guardar_administrador_faz_rollback_se_falhar(self):
        admin_in = Administrador(id_admin=None, username="admin", password_hash="hashed_password")
        self.cursor_mock.execute.side_effect = Exception("Erro SQL")

        with self.assertRaisesRegex(Exception, "Erro SQL"):
            AdministradorRepository(self.conexao_mock).guardar_administrador(admin_in)

        self.conexao_mock.rollback.assert_called_once()
        self.conexao_mock.commit.assert_not_called()
        
    def test_atualizar_password(self):
        self.cursor_mock.rowcount = 1
        atualizado = AdministradorRepository(self.conexao_mock).atualizar_password(1, "new_hashed_password")

        self.assertTrue(atualizado)
        self.cursor_mock.execute.assert_called_once()
        self.conexao_mock.commit.assert_called_once()
        self.conexao_mock.rollback.assert_not_called()

    def test_atualizar_password_sem_id(self):
        self.cursor_mock.rowcount = 0
        atualizado = AdministradorRepository(self.conexao_mock).atualizar_password(999, "new_hashed_password")

        self.assertFalse(atualizado)
        self.cursor_mock.execute.assert_called_once()
        self.conexao_mock.commit.assert_called_once()
        self.conexao_mock.rollback.assert_not_called()

    def test_atualizar_password_faz_rollback_se_falhar(self):
        self.cursor_mock.execute.side_effect = Exception("Erro SQL")

        with self.assertRaisesRegex(Exception, "Erro SQL"):
            AdministradorRepository(self.conexao_mock).atualizar_password(1, "new_hashed_password")

        self.conexao_mock.rollback.assert_called_once()
        self.conexao_mock.commit.assert_not_called()

    def test_username_existe(self):
        self.cursor_mock.fetchone.return_value = {"existe": True}
        existe = AdministradorRepository(self.conexao_mock).username_existe("admin")

        self.assertTrue(existe)
        self.cursor_mock.execute.assert_called_once()

    def test_username_nao_existe(self):
        self.cursor_mock.fetchone.return_value = {"existe": False}
        existe = AdministradorRepository(self.conexao_mock).username_existe("outro")

        self.assertFalse(existe)

    def test_procurar_por_username_normaliza_maiusculas(self):
        self.cursor_mock.fetchone.return_value = None
        AdministradorRepository(self.conexao_mock).procurar_por_username("  ADMIN ")

        parametros = self.cursor_mock.execute.call_args[0][1]
        self.assertEqual(parametros, ("admin",))

if __name__ == "__main__":
    unittest.main()