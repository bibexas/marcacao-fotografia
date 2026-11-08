from marcacao_fotografia.domain.pedido import Pedido
from marcacao_fotografia.domain.estado_pedido import EstadoPedido

class PedidoRepository:

    def __init__(self, conexao):
        self.conexao = conexao

    def linha_para_pedido(self, linha: dict) -> Pedido:
        return Pedido(
            id_pedido=linha["id_pedido"],
            codigo_consulta=linha["codigo_consulta"],
            data_sessao=linha["data_sessao"],
            hora_inicio=linha["hora_inicio"],
            hora_fim=linha["hora_fim"],
            localizacao=linha["localizacao"],
            duracao=linha["duracao"],
            estado=EstadoPedido(linha["estado"]),
            observacoes=linha["observacoes"],
            id_cliente=linha["id_cliente"],
            id_tipo=linha["id_tipo"],
        )

    def guardar_pedido(self, pedido: Pedido) -> Pedido:
        query = """
        INSERT INTO pedido (codigo_consulta, data_sessao, hora_inicio, hora_fim, localizacao, duracao, estado, observacoes, id_cliente, id_tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_pedido
        """
        with self.conexao.cursor() as cursor:
            cursor.execute(
                query,
                (
                    pedido.codigo_consulta,
                    pedido.data_sessao,
                    pedido.hora_inicio,
                    pedido.hora_fim,
                    pedido.localizacao,
                    pedido.duracao,
                    pedido.estado.value,
                    pedido.observacoes,
                    pedido.id_cliente,
                    pedido.id_tipo,
                ),
            )
            resultado = cursor.fetchone()
            novo_id = resultado["id_pedido"]

        return Pedido(
            id_pedido=novo_id,
            codigo_consulta=pedido.codigo_consulta,
            data_sessao=pedido.data_sessao,
            hora_inicio=pedido.hora_inicio,
            hora_fim=pedido.hora_fim,
            localizacao=pedido.localizacao,
            duracao=pedido.duracao,
            estado=pedido.estado,
            observacoes=pedido.observacoes,
            id_cliente=pedido.id_cliente,
            id_tipo=pedido.id_tipo,
        )

    def procurar_codigo(self, codigo_consulta: str) -> Pedido | None:
        query = "SELECT * FROM pedido WHERE codigo_consulta = %s"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (codigo_consulta.strip(),))
            linha = cursor.fetchone()
        if linha is None:
            return None

        return self.linha_para_pedido(linha)

    def listar_todos(self) -> list[Pedido]:
        query = "SELECT * FROM pedido"
        with self.conexao.cursor() as cursor:
            cursor.execute(query)
            linhas = cursor.fetchall()

        return [self.linha_para_pedido(linha) for linha in linhas]

    def consultar_sobreposicoes(self, data_sessao, hora_inicio, hora_fim) -> list[Pedido]:
        query = """
        SELECT * FROM pedido
        WHERE data_sessao = %s
            AND estado = %s
            AND hora_inicio < %s
            AND hora_fim > %s
        """
        with self.conexao.cursor() as cursor:
            cursor.execute(
                query,
                (
                    data_sessao,
                    EstadoPedido.CONFIRMADA.value,                
                    hora_inicio,
                    hora_fim,
                ),
            )
            linhas = cursor.fetchall()

        return [self.linha_para_pedido(linha) for linha in linhas]

    def atualizar_estado(self, id_pedido: int, novo_estado: EstadoPedido) -> None:
        query = "UPDATE pedido SET estado = %s WHERE id_pedido = %s"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (novo_estado.value, id_pedido))

    
