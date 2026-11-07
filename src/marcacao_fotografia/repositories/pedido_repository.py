from __future__ import annotations

from typing import Any

from marcacao_fotografia.database import obter_conexao
from marcacao_fotografia.domain.pedido import Pedido


class PedidoRepository:
    def _para_modelo(self, row: dict[str, Any] | None) -> Pedido | None:
        if row is None:
            return None
        return Pedido(
            id_pedido=row.get("id_pedido"),
            codigo_consulta=row.get("codigo_consulta"),
            data_sessao=row.get("data_sessao"),
            hora_inicio=row.get("hora_inicio"),
            hora_fim=row.get("hora_fim"),
            localizacao=row.get("localizacao"),
            duracao=row.get("duracao"),
            estado=row.get("estado", "pendente"),
            observacoes=row.get("observacoes"),
            id_cliente=row.get("id_cliente"),
            id_tipo=row.get("id_tipo"),
        )

    def salvar(self, pedido: Pedido) -> Pedido:
        pedido.validar()

        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                if pedido.id_pedido is None:
                    cursor.execute(
                        """
                        INSERT INTO pedido (
                            codigo_consulta, data_sessao, hora_inicio, hora_fim,
                            localizacao, duracao, estado, observacoes, id_cliente, id_tipo
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id_pedido
                        """,
                        (
                            pedido.codigo_consulta,
                            pedido.data_sessao,
                            pedido.hora_inicio,
                            pedido.hora_fim,
                            pedido.localizacao,
                            pedido.duracao,
                            pedido.estado,
                            pedido.observacoes,
                            pedido.id_cliente,
                            pedido.id_tipo,
                        ),
                    )
                    resultado = cursor.fetchone()
                    pedido.id_pedido = resultado["id_pedido"] if resultado else pedido.id_pedido
                else:
                    cursor.execute(
                        """
                        UPDATE pedido
                        SET codigo_consulta = %s,
                            data_sessao = %s,
                            hora_inicio = %s,
                            hora_fim = %s,
                            localizacao = %s,
                            duracao = %s,
                            estado = %s,
                            observacoes = %s,
                            id_cliente = %s,
                            id_tipo = %s
                        WHERE id_pedido = %s
                        """,
                        (
                            pedido.codigo_consulta,
                            pedido.data_sessao,
                            pedido.hora_inicio,
                            pedido.hora_fim,
                            pedido.localizacao,
                            pedido.duracao,
                            pedido.estado,
                            pedido.observacoes,
                            pedido.id_cliente,
                            pedido.id_tipo,
                            pedido.id_pedido,
                        ),
                    )
            conexao.commit()
            return pedido
        finally:
            conexao.close()

    def buscar_por_id(self, id_pedido: int) -> Pedido | None:
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM pedido WHERE id_pedido = %s", (id_pedido,))
                row = cursor.fetchone()
            return self._para_modelo(row)
        finally:
            conexao.close()

    def buscar_por_codigo_consulta(self, codigo_consulta: str) -> Pedido | None:
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM pedido WHERE codigo_consulta = %s",
                    (codigo_consulta,),
                )
                row = cursor.fetchone()
            return self._para_modelo(row)
        finally:
            conexao.close()

    def listar_todos(self) -> list[Pedido]:
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM pedido ORDER BY data_sessao, hora_inicio")
                rows = cursor.fetchall()
            return [self._para_modelo(row) for row in rows if row is not None]
        finally:
            conexao.close()

    def remover(self, id_pedido: int) -> bool:
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM pedido WHERE id_pedido = %s", (id_pedido,))
            conexao.commit()
            return cursor.rowcount > 0
        finally:
            conexao.close()

    def codigo_consulta_existe(self, codigo_consulta: str) -> bool:
        conexao = obter_conexao()
        try:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM pedido WHERE codigo_consulta = %s)",
                    (codigo_consulta,),
                )
                resultado = cursor.fetchone()
                if resultado is None:
                    return False
                return bool(resultado.get("exists", False))
        finally:
            conexao.close()
