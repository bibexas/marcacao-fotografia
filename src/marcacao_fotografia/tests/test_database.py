import unittest
from unittest.mock import MagicMock, patch

from marcacao_fotografia import database


class TestDatabase(unittest.TestCase):
    def test_sem_database_url_levanta_erro(self):
        with patch.object(database, "DATABASE_URL", None):
            with self.assertRaises(ValueError):
                database.obter_conexao()
                
    def test_ligacao_com_sucesso(self):
        with patch.object(database, "DATABASE_URL", "postgresql://user:password@localhost/testdb"):
            with patch("marcacao_fotografia.database.psycopg.connect") as mock_connect:
                mock_connect.return_value = MagicMock()
                conn = database.obter_conexao()
                self.assertIsNotNone(conn)
                mock_connect.assert_called_once_with(
                    "postgresql://user:password@localhost/testdb",
                    row_factory=database.dict_row,
                )

    def test_rollback_em_caso_de_erro(self):
        with patch.object(database, "DATABASE_URL", "postgresql://user:password@localhost/testdb"):
            with patch("marcacao_fotografia.database.psycopg.connect") as mock_connect:
                with patch("marcacao_fotografia.database.Path.read_text", return_value="SELECT 1;"):
                    mock_conn = MagicMock()
                    mock_connect.return_value = mock_conn
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
                    mock_cursor.execute.side_effect = Exception("Erro ao executar SQL")
                
                    with self.assertRaisesRegex(Exception, "Erro ao executar SQL"):
                        database.iniciar_bd()
                mock_conn.rollback.assert_called_once()
                mock_conn.close.assert_called_once()
                mock_conn.commit.assert_not_called()