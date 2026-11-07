from dataclasses import dataclass

class DadosTipoEventoInvalidos(ValueError):
    pass

@dataclass(frozen=True)
class TipoEvento:
    id_tipo: int | None
    tipo: str

    def __post_init__(self):
        tipo_limpo = self.tipo.strip()

        if not tipo_limpo:
            raise DadosTipoEventoInvalidos("O tipo de evento não pode estar vazio.")

        object.__setattr__(self, "tipo", tipo_limpo)
    