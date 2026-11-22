import hmac
import threading
import time as time_module
from flask import session, request, abort

_limites: dict[tuple[str, str], list[float]] = {}
_limites_lock = threading.Lock()


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
    agora = time_module.monotonic()
    chave = (request.remote_addr or "desconhecido", nome_rota)
    with _limites_lock:
        for chave_antiga, instantes in list(_limites.items()):
            recentes = [
                instante
                for instante in instantes
                if agora - instante < 60
            ]
            if recentes:
                _limites[chave_antiga] = recentes
            else:
                del _limites[chave_antiga]

        pedidos_recentes = [
            instante
            for instante in _limites.get(chave, [])
            if agora - instante < 60
        ]
        if len(pedidos_recentes) >= limite:
            _limites[chave] = pedidos_recentes
            return False

        pedidos_recentes.append(agora)
        _limites[chave] = pedidos_recentes
        return True
        
