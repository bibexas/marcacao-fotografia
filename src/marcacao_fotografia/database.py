from pathlib import Path

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - depends on the runtime environment
    psycopg = None
    dict_row = None

from marcacao_fotografia.config import DATABASE_URL


def obter_conexao():
    if psycopg is None or dict_row is None:
        raise RuntimeError(
            "A dependência psycopg não está disponível no ambiente atual. "
            "Instale os requisitos do projeto antes de usar o banco de dados."
        )
    if not DATABASE_URL:
        raise ValueError("A variável de ambiente DATABASE_URL não está definida.")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


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

def testar_conexao():
    try:
        conexao = obter_conexao()
    except Exception:
        return False
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT 1;")
            return True
    except Exception:
        return False
    finally:
        conexao.close()
