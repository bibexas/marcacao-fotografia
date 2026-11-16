from datetime import date, time
import unittest

from marcacao_fotografia.domain.pedido import Pedido, DadosPedidoInvalidos
from marcacao_fotografia.domain.estado_pedido import EstadoPedido
from marcacao_fotografia.domain.cliente import Cliente, DadosClienteInvalidos
from marcacao_fotografia.domain.tipo_evento import TipoEvento
from marcacao_fotografia.domain.administrador import Administrador, DadosAdministradorInvalidos

class TestDomain(unittest.TestCase):
    def test_criar_cliente_valido(self):
        cliente = Cliente(
            id_cliente=None,
            nome="Beatriz Vilaça",
            email="abeatrizvg@gmail.com",
            telefone="912345678",
        )
        self.assertEqual(cliente.nome, "Beatriz Vilaça")
        self.assertEqual(cliente.email, "abeatrizvg@gmail.com")
        self.assertEqual(cliente.telefone, "912345678")

    def test_rejeitar_cliente_sem_nome(self):
        with self.assertRaisesRegex(DadosClienteInvalidos, "O nome não pode estar vazio."):
            Cliente(
                id_cliente=None,
                nome="",
                email="abeatrizvg@gmail.com",
                telefone="912345678",
            )

    def test_rejeitar_cliente_email_invalido(self):
        with self.assertRaisesRegex(DadosClienteInvalidos, "O email fornecido é inválido."):
            Cliente(
                id_cliente=None,
                nome="Beatriz Vilaça",
                email="abeatrizvg@gmail",
                telefone="912345678",
            )

    def test_criar_pedido_e_calculo_duracao(self):
        pedido = Pedido(
            id_pedido=None,
            codigo_consulta="ABC12345",
            data_sessao=date(2024, 6, 15),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0),
            localizacao="Estúdio Fotográfico",
            estado=EstadoPedido.PENDENTE,
            observacoes="Sessão de fotos para evento corporativo",
            id_cliente=1,
            id_tipo=1,
        )
        self.assertEqual(pedido.codigo_consulta, "ABC12345")
        self.assertEqual(pedido.duracao, 120)
        self.assertTrue(pedido.cliente_cancelar())

    def test_rejeitar_pedido_com_hora_fim_antes_hora_inicio(self):
        with self.assertRaisesRegex(DadosPedidoInvalidos, "A hora de fim deve ser posterior à hora de início"):
            Pedido(
                id_pedido=None,
                codigo_consulta="ABC12345",
                data_sessao=date(2024, 6, 15),
                hora_inicio=time(12, 0),
                hora_fim=time(10, 0),
                localizacao="Estúdio Fotográfico",
                estado=EstadoPedido.PENDENTE,
                observacoes=None,
                id_cliente=1,
                id_tipo=1,
            )

    def test_rejeitar_codigo_consulta_invalido(self):
        with self.assertRaisesRegex(DadosPedidoInvalidos, "O código de consulta deve ter 8 caracteres."):
            Pedido(
                id_pedido=None,
                codigo_consulta="ABC1234",
                data_sessao=date(2024, 6, 15),
                hora_inicio=time(10, 0),
                hora_fim=time(12, 0),
                localizacao="Estúdio Fotográfico",
                estado=EstadoPedido.PENDENTE,
                observacoes=None,
                id_cliente=1,
                id_tipo=1,
            )

    def test_regras_cancelamento_pedido(self):
        pedido = Pedido(
            id_pedido=None,
            codigo_consulta="ABC12345",
            data_sessao=date(2024, 6, 15),
            hora_inicio=time(10, 0),
            hora_fim=time(12, 0),
            localizacao="Estúdio Fotográfico",
            estado=EstadoPedido.PENDENTE,
            observacoes=None,
            id_cliente=1,
            id_tipo=1,
        )
        self.assertTrue(pedido.cliente_cancelar())
        self.assertTrue(pedido.equipa_cancelar())

        pedido_confirmado = Pedido(
            id_pedido=2,
            codigo_consulta="DEF67890",
            data_sessao=date(2024, 6, 16),
            hora_inicio=time(14, 0),
            hora_fim=time(16, 0),
            localizacao="Estúdio Fotográfico",
            estado=EstadoPedido.CONFIRMADA,
            observacoes=None,
            id_cliente=2,
            id_tipo=2,
        )
        self.assertFalse(pedido_confirmado.cliente_cancelar())
        self.assertTrue(pedido_confirmado.equipa_cancelar())

    def test_username_vazio_rejeitado(self):
        with self.assertRaisesRegex(DadosAdministradorInvalidos, "não pode estar vazio"):
            Administrador.criar(username="", password="password123")

    def test_username_com_mais_de_50_caracteres_rejeitado(self):
        with self.assertRaisesRegex(DadosAdministradorInvalidos, "mais de 50 caracteres"):
            Administrador.criar(username="a" * 51, password="password123")

    def test_username_com_espacos_rejeitado(self):
        with self.assertRaisesRegex(DadosAdministradorInvalidos, "não pode conter espaços"):
            Administrador.criar(username="user name", password="password123")

    def test_password_curta_rejeitada(self):
        with self.assertRaisesRegex(DadosAdministradorInvalidos, "pelo menos 8 caracteres"):
            Administrador.criar(username="user123", password="pass")

    def test_hash_guardado_difere_da_password(self):
        admin = Administrador.criar(username="user123", password="password123")
        self.assertNotEqual(admin.password_hash, "password123")

    def test_verificar_password_certa_e_errada(self):
        admin = Administrador.criar(username="user123", password="password123")
        self.assertTrue(admin.verificar_password("password123"))
        self.assertFalse(admin.verificar_password("wrongpassword"))

    def test_hash_vazio_rejeitado(self):
        with self.assertRaisesRegex(DadosAdministradorInvalidos, "hash da password"):
            Administrador(id_admin=None, username="user123", password_hash="")

    def test_password_vazia_nao_verifica(self):
        admin = Administrador.criar(username="user123", password="password123")
        self.assertFalse(admin.verificar_password(""))

    def test_repr_sem_hash_da_password(self):
        admin = Administrador.criar(username="user123", password="password123")
        self.assertNotIn(admin.password_hash, repr(admin))
        self.assertIn("Administrador(id_admin=None, username='user123')", repr(admin))

if __name__ == "__main__":
    unittest.main()