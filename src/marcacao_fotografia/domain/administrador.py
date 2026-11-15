from dataclasses import dataclass
from werkzeug.security import check_password_hash, generate_password_hash


class DadosAdministradorInvalidos(ValueError):
    pass


@dataclass(frozen=True)
class Administrador:
    id_admin: int | None
    username: str
    password_hash: str

    def __post_init__(self):
        username_limpo = self.username.strip()
        password_hash_limpo = self.password_hash.strip()

        # Validar os dados do administrador
        if not username_limpo:
            raise DadosAdministradorInvalidos("O username não pode estar vazio.")
        if not password_hash_limpo:
            raise DadosAdministradorInvalidos("A password não pode estar vazia.")

        # Atribuir os valores limpos aos atributos do objeto
        object.__setattr__(self, "username", username_limpo)
        object.__setattr__(self, "password_hash", password_hash_limpo)

    @classmethod
    def criar(cls, username: str, password: str) -> "Administrador":
        username_limpo = username.strip()
        password_hash = generate_password_hash(password)

        return cls(id_admin=None, username=username_limpo, password_hash=password_hash)

    def verificar_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password.strip())