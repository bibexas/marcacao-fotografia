import hmac
from flask import session, request, abort
from marcacao_fotografia.database import obter_conexao


def validar_csrf() -> None:
        token_atual = session.get("_csrf_token")
        token_recebido = request.form.get("_csrf_token", "")
        if (
            not token_atual
            or not token_recebido
            or not hmac.compare_digest(token_atual, token_recebido)
        ):
            abort(400, description="Token CSRF inválido ou ausente.")

def permitir_requisicao(nome_rota: str, limite: int) -> bool:
    conexao = obter_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO limite_requisicao (chave, rota, inicio_janela, contagem)
                VALUES (%s, %s, CURRENT_TIMESTAMP, 1)
                ON CONFLICT (chave, rota) DO UPDATE
                SET inicio_janela = CASE
                        WHEN CURRENT_TIMESTAMP - limite_requisicao.inicio_janela
                            >= INTERVAL '1 minute'
                        THEN CURRENT_TIMESTAMP
                        ELSE limite_requisicao.inicio_janela
                    END,
                    contagem = CASE
                        WHEN CURRENT_TIMESTAMP - limite_requisicao.inicio_janela
                            >= INTERVAL '1 minute'
                        THEN 1
                        ELSE limite_requisicao.contagem + 1
                    END
                RETURNING contagem
                """,
                (request.remote_addr or "desconhecido", nome_rota),
            )
            contagem = cursor.fetchone()["contagem"]
        conexao.commit()
        return contagem <= limite
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
