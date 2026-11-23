import getpass

from marcacao_fotografia.database import obter_conexao
from marcacao_fotografia.domain.administrador import Administrador, DadosAdministradorInvalidos
from marcacao_fotografia.repositories.administrador_repository import AdministradorRepository


def main():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    confirmacao = getpass.getpass("Confirmar password: ")

    if password != confirmacao:
        print("Erro ao criar administrador: As passwords não coincidem.")
        return

    try:
        administrador = Administrador.criar(username, password)
    except DadosAdministradorInvalidos as e:
        print(f"Erro ao criar administrador: {e}")
        return

    conexao = obter_conexao()
    try:
        repository = AdministradorRepository(conexao)

        if repository.username_existe(administrador.username):
            print("Erro ao criar administrador: Já existe um administrador com esse username.")
            return

        repository.guardar_administrador(administrador)
        print("Administrador criado com sucesso.")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
