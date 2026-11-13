from marcacao_fotografia.domain.cliente import Cliente

class ClienteRepository:
    def __init__(self, conexao):
        
        self.conexao = conexao

    def guardar_cliente(self, cliente: Cliente) -> Cliente:
        query = """
        INSERT INTO cliente (nome, email, telefone)
        VALUES (%s, %s, %s)
        RETURNING id_cliente
        """
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (cliente.nome, cliente.email, cliente.telefone))
            resultado = cursor.fetchone()
            novo_id = resultado["id_cliente"]
        self.conexao.commit()

        return Cliente(id_cliente=novo_id, nome=cliente.nome, email=cliente.email, telefone=cliente.telefone)

    def procurar_email(self, email: str) -> Cliente | None:
        query = "SELECT * FROM cliente WHERE email = %s"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (email.strip(),))
            linha = cursor.fetchone()
        if linha is None:
            return None

        return Cliente(
            id_cliente=linha["id_cliente"],
            nome=linha["nome"],
            email=linha["email"],
            telefone=linha["telefone"],
        )
    def procurar_id(self, id_cliente: int) -> Cliente | None:
        query = "SELECT * FROM cliente WHERE id_cliente = %s"
        with self.conexao.cursor() as cursor:
            cursor.execute(query, (id_cliente,))
            linha = cursor.fetchone()
        if linha is None:
            return None

        return Cliente(
            id_cliente=linha["id_cliente"],
            nome=linha["nome"],
            email=linha["email"],
            telefone=linha["telefone"],
        )