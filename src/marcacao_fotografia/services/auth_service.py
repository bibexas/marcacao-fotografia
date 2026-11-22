from marcacao_fotografia.domain.administrador import Administrador
from marcacao_fotografia.repositories.administrador_repository import AdministradorRepository

MENSAGEM_LOGIN_INVALIDO ="Credenciais inválidas. Por favor, tente novamente."

class CredenciaisInvalidasError(Exception):
    pass

class AdministradorNaoEncontradoError(Exception):
    pass

class AuthService:
    def __init__(self, administrador_repo: AdministradorRepository):
        self.administrador_repo = administrador_repo

    # Validar as credenciais e devolver o administrador autenticado
    def login(self, username: str, password: str) -> Administrador:
        username = username.strip()
        if not username or not password:
            raise CredenciaisInvalidasError(MENSAGEM_LOGIN_INVALIDO)

        administrador = self.administrador_repo.procurar_por_username(username)
        if not administrador or not administrador.verificar_password(password):
            raise CredenciaisInvalidasError(MENSAGEM_LOGIN_INVALIDO)
        
        return administrador

    def obter_administrador_por_id(self, id_admin: int) -> Administrador:
        administrador = self.administrador_repo.procurar_id(id_admin)
        if not administrador:
            raise AdministradorNaoEncontradoError(f"Administrador com o ID {id_admin} não foi encontrado.")
        return administrador