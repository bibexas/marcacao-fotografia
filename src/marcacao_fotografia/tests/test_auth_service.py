import unittest
from unittest.mock import MagicMock

from marcacao_fotografia.domain.administrador import Administrador
from marcacao_fotografia.repositories.administrador_repository import AdministradorRepository
from marcacao_fotografia.services.auth_service import (AuthService, CredenciaisInvalidasError, AdministradorNaoEncontradoError, MENSAGEM_LOGIN_INVALIDO,)

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock(spec=AdministradorRepository)
        self.admin = Administrador.criar("admin", "password123")
        self.service = AuthService(self.repo)

    def test_login_valido(self):
        self.repo.procurar_por_username.return_value = self.admin

        resultado = self.service.login("admin", "password123")

        self.assertEqual(resultado.username, "admin")
        self.repo.procurar_por_username.assert_called_once_with("admin")

    def test_password_errada(self):
        self.repo.procurar_por_username.return_value = self.admin

        with self.assertRaises(CredenciaisInvalidasError):
            self.service.login("admin", "errada123")

    def test_username_inexistente(self):
        self.repo.procurar_por_username.return_value = None

        with self.assertRaises(CredenciaisInvalidasError):
            self.service.login("naoexiste", "password123")

    def test_mensagem_erro(self):
        self.repo.procurar_por_username.return_value = self.admin
        with self.assertRaises(CredenciaisInvalidasError) as ctx_password:
            self.service.login("admin", "errada123")

        self.repo.procurar_por_username.return_value = None
        with self.assertRaises(CredenciaisInvalidasError) as ctx_username:
            self.service.login("naoexiste", "password123")

        self.assertEqual(str(ctx_password.exception), str(ctx_username.exception))
        self.assertEqual(str(ctx_password.exception), MENSAGEM_LOGIN_INVALIDO)

    def test_credenciais_vazias(self):
        casos = [("", "password123"), ("admin", ""), ("", "")]
        for username, password in casos:
            with self.subTest(username=username, password=password):
                with self.assertRaises(CredenciaisInvalidasError):
                    self.service.login(username, password)

        self.repo.procurar_por_username.assert_not_called()

    def test_obter_administrador_por_id(self):
        self.repo.procurar_id.return_value = self.admin

        resultado = self.service.obter_administrador_por_id(1)

        self.assertEqual(resultado.username, "admin")

    def test_obter_administrador_por_id_inexistente(self):
        self.repo.procurar_id.return_value = None

        with self.assertRaises(AdministradorNaoEncontradoError):
            self.service.obter_administrador_por_id(999)

    if __name__ == "__main__":
        unittest.main()