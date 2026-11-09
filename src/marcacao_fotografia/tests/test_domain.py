from datetime import date, time
import unittest

from marcacao_fotografia.domain.pedido import Pedido, DadosPedidoInvalidos
from marcacao_fotografia.domain.estado_pedido import EstadoPedido
from marcacao_fotografia.domain.cliente import Cliente, DadosClienteInvalidos
from marcacao_fotografia.domain.tipo_evento import TipoEvento

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
        with self.assertRaises(DadosClienteInvalidos):
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

if __name__ == "__main__":
    unittest.main()