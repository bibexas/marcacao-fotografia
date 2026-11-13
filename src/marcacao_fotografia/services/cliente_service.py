from marcacao_fotografia.domain.cliente import Cliente, DadosClienteInvalidos
from marcacao_fotografia.repositories.cliente_repository import ClienteRepository

class EmailJaExisteError(ValueError):
    pass

class ClienteNaoEncontradoError(ValueError):
    pass

class ClienteService:
    def __init__(self, cliente_repo: ClienteRepository):
        self.cliente_repo = cliente_repo

    def criar_cliente(self, nome: str, email: str, telefone: str) -> Cliente:
        email_limpo = email.strip()
        cliente_existente = self.cliente_repo.procurar_email(email_limpo)
        if cliente_existente:
            raise EmailJaExisteError(f"Já existe um cliente registado com o email '{email_limpo}'.")

        novo_cliente = Cliente(
            id_cliente=None,
            nome=nome,
            email=email_limpo,
            telefone=telefone
        )
        return self.cliente_repo.guardar_cliente(novo_cliente)

    def obter_cliente_por_id(self, id_cliente: int) -> Cliente:
        cliente = self.cliente_repo.procurar_id(id_cliente)
        if not cliente:
            raise ClienteNaoEncontradoError(f"Cliente com o ID {id_cliente} não foi encontrado.")
        return cliente

    def obter_cliente_por_email(self, email: str) -> Cliente:
        cliente = self.cliente_repo.procurar_email(email.strip())
        if not cliente:
            raise ClienteNaoEncontradoError(f"Cliente com o email '{email}' não foi encontrado.")
        return cliente

    