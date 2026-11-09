from marcacao_fotografia.domain.tipo_evento import TipoEvento

class TipoEventoRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    def listar_tipos_evento(self) -> list[TipoEvento]:
        query = "SELECT * FROM tipo_evento ORDER BY tipo ASC"
        with self.conexao.cursor() as cursor:
            cursor.execute(query)
            linhas = cursor.fetchall()

        return [
            TipoEvento(
                id_tipo=linha["id_tipo"],
                tipo=linha["tipo"]
            )
            for linha in linhas
        ]

    def procurar_por_id(self, id_tipo: int) -> TipoEvento | None:
        query = "SELECT * FROM tipo_evento WHERE id_tipo = %s"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (id_tipo,))
            linha = cursor.fetchone()
        if linha is None:
            return None

        return TipoEvento(
            id_tipo=linha["id_tipo"],
            tipo=linha["tipo"]
        )
