from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

from marcacao_fotografia.config import DATABASE_URL


def obter_conexao():
    if not DATABASE_URL:
        raise ValueError("A variável de ambiente DATABASE_URL não está definida.")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def iniciar_bd():
    """Create the database tables defined in docs/schema.sql if needed."""
    caminho_schema = Path(__file__).resolve().parents[2] / "docs" / "schema.sql"
    sql_schema = caminho_schema.read_text(encoding="utf-8")

    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql_schema)
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
