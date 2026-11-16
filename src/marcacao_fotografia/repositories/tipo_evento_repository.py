import unicodedata

from marcacao_fotografia.domain.tipo_evento import TipoEvento

class TipoEventoRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    # Listar todos os tipos de evento
    def listar_tipos_evento(self) -> list[TipoEvento]:
        query = """
        SELECT id_tipo, tipo
        FROM tipo_evento
        ORDER BY tipo ASC, id_tipo ASC
        """
        with self.conexao.cursor() as cursor:
            cursor.execute(query)
            linhas = cursor.fetchall()

        tipos_vistos = set()
        tipos = []
        for linha in linhas:
            nome_normalizado = unicodedata.normalize("NFKC", linha["tipo"]).strip().casefold()
            if nome_normalizado in tipos_vistos:
                continue
            tipos_vistos.add(nome_normalizado)
            tipos.append(TipoEvento(id_tipo=linha["id_tipo"], tipo=linha["tipo"]))
        return tipos

    # Procurar um tipo de evento pelo ID
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

    # Procurar um tipo de evento pelo nome
    def procurar_por_nome(self, tipo: str) -> TipoEvento | None:
        query = """
        SELECT id_tipo, tipo
        FROM tipo_evento
        WHERE LOWER(BTRIM(tipo)) = LOWER(BTRIM(%s))
        ORDER BY id_tipo ASC
        LIMIT 1
        """
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (tipo.strip(),))
            linha = cursor.fetchone()
        if linha is None:
            return None

        return TipoEvento(id_tipo=linha["id_tipo"], tipo=linha["tipo"])

    # Guardar um tipo de evento na base de dados
    def guardar(self, tipo_evento: TipoEvento) -> TipoEvento:
        query = """
        INSERT INTO tipo_evento (tipo)
        VALUES (%s)
        RETURNING id_tipo
        """
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(query, (tipo_evento.tipo,))
                resultado = cursor.fetchone()
                novo_id = resultado["id_tipo"]
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise

        return TipoEvento(id_tipo=novo_id, tipo=tipo_evento.tipo)
