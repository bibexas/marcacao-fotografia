from functools import wraps

from flask import g, redirect, session, url_for

from marcacao_fotografia.services.auth_service import AdministradorNaoEncontradoError
from marcacao_fotografia.web.servicos import obter_servicos

def login_required(vista):
    @wraps(vista)
    def embrulho(*args, **kwargs):
        id_admin = session.get("id_admin")
        if id_admin is None:
            return redirect(url_for("auth.login"))

        try:
            administrador = obter_servicos().auth.obter_administrador_por_id(id_admin)
        except AdministradorNaoEncontradoError:
                session.clear()
                return redirect(url_for("auth.login"))

        g.administrador = administrador
        return vista(*args, **kwargs)

    return embrulho
        