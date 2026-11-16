from marcacao_fotografia.domain.administrador import Administrador


class AdministradorRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    # Procurar um administrador pelo username
    def procurar_por_username(self, username: str) -> Administrador | None:
        query = "SELECT * FROM administrador WHERE username = %s"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (username.strip().lower(),))
            linha = cursor.fetchone()
        if linha is None:
            return None

        return Administrador(
            id_admin=linha["id_admin"],
            username=linha["username"],
            password_hash=linha["password_hash"],
        )

    # Guardar um administrador na base de dados
    def guardar_administrador(self, administrador: Administrador) -> Administrador:
        query = """
        INSERT INTO administrador (username, password_hash)
        VALUES (%s, %s)
        RETURNING id_admin
        """
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    query, (administrador.username, administrador.password_hash)
                )
                resultado = cursor.fetchone()
                novo_id = resultado["id_admin"]
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        return Administrador(id_admin=novo_id, username=administrador.username, password_hash=administrador.password_hash)

    # Atualizar a password de um administrador
    def atualizar_password(self, id_admin: int, nova_password_hash: str) -> bool:
        query = "UPDATE administrador SET password_hash = %s WHERE id_admin = %s"
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(query, (nova_password_hash, id_admin))
                atualizada = cursor.rowcount > 0
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        return atualizada

    # Username já existe na base de dados
    def username_existe(self, username: str) -> bool:
        query = "SELECT EXISTS (SELECT 1 FROM administrador WHERE username = %s) AS existe"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (username.strip().lower(),))
            return cursor.fetchone() ["existe"]