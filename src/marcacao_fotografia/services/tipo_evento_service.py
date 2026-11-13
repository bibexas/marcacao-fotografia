from marcacao_fotografia.domain.tipo_evento import TipoEvento
from marcacao_fotografia.repositories.tipo_evento_repository import TipoEventoRepository

class TipoEventoNaoEncontradoError(ValueError):
    pass

class TipoEventoJaExisteError(ValueError):
    pass

class TipoEventoService:
    def __init__(self, tipo_evento_repo: TipoEventoRepository):
        self.tipo_evento_repo = tipo_evento_repo

    def listar_tipos_evento(self) -> list[TipoEvento]:
        return self.tipo_evento_repo.listar_tipos_evento()

    def obter_tipo_evento_por_id(self, id_tipo: int) -> TipoEvento:
        tipo_evento = self.tipo_evento_repo.procurar_por_id(id_tipo)
        if not tipo_evento:
            raise TipoEventoNaoEncontradoError(f"Tipo de evento com ID {id_tipo} não encontrado.")
        return tipo_evento

    def criar_tipo_evento(self, tipo: str) -> TipoEvento:
        tipo_limpo = tipo.strip()
        if self.tipo_evento_repo.procurar_por_nome(tipo_limpo):
            raise TipoEventoJaExisteError(f"O tipo de evento '{tipo_limpo}' já existe.")
        
        novo_tipo = TipoEvento(id_tipo=None, tipo=tipo_limpo)
        return self.tipo_evento_repo.guardar(novo_tipo)