from dataclasses import dataclass

class DadosClienteInvaliados(ValueError):
    pass

@dataclass(frozen=True)
class Cliente:
    id_cliente: int | None
    nome: str
    email: str
    telefone: str

    def __post_init__(self):
        nome_limpo = self.nome.strip()
        email_limpo = self.email.strip()
        telefone_limpo = self.telefone.strip()

        if not nome_limpo:
            raise DadosClienteInvaliados("O nome não pode estar vazio.")
        if not email_limpo or "@" not in email_limpo:
            raise DadosClienteInvaliados("O email fornecido é inválido.")
        if not telefone_limpo or not telefone_limpo.isdigit():
            raise DadosClienteInvaliados("O telefone fornecido é inválido.")

        object.__setattr__(self, "nome", nome_limpo)
        object.__setattr__(self, "email", email_limpo)
        object.__setattr__(self, "telefone", telefone_limpo)