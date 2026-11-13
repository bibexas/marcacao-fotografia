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

    def procurar_por_nome(self, tipo: str) -> TipoEvento | None:
        query = "SELECT * FROM tipo_evento WHERE tipo = %s"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (tipo.strip(),))
            linha = cursor.fetchone()
        if linha is None:
            return None

        return TipoEvento(id_tipo=linha["id_tipo"], tipo=linha["tipo"])

    def guardar(self, tipo_evento: TipoEvento) -> TipoEvento:
        query = """
        INSERT INTO tipo_evento (tipo)
        VALUES (%s)
        RETURNING id_tipo
        """
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (tipo_evento.tipo,))
            resultado = cursor.fetchone()
            novo_id = resultado["id_tipo"]
        self.conexao.commit()

        return TipoEvento(id_tipo=novo_id, tipo=tipo_evento.tipo)
