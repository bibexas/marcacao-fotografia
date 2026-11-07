from __future__ import annotations

import random
import string
from dataclasses import dataclass
from datetime import date, time
from typing import Any


ESTADOS_PEDIDO = {"pendente", "confirmado", "cancelado", "concluido"}


def gerar_codigo_consulta() -> str:
    letras = "".join(random.choices(string.ascii_uppercase, k=3))
    numeros = "".join(random.choices(string.digits, k=4))
    return f"{letras}-{numeros}"


@dataclass
class Pedido:
    id_pedido: int | None = None
    codigo_consulta: str | None = None
    data_sessao: date | str | None = None
    hora_inicio: time | str | None = None
    hora_fim: time | str | None = None
    localizacao: str | None = None
    duracao: int = 0
    estado: str = "pendente"
    observacoes: str | None = None
    id_cliente: int | None = None
    id_tipo: int | None = None

    def __post_init__(self) -> None:
        if self.codigo_consulta is None or not self.codigo_consulta.strip():
            self.codigo_consulta = gerar_codigo_consulta()

        self.data_sessao = self._converter_data(self.data_sessao)
        self.hora_inicio = self._converter_hora(self.hora_inicio)
        self.hora_fim = self._converter_hora(self.hora_fim)
        self.estado = (self.estado or "pendente").strip().lower()

    @staticmethod
    def _converter_data(valor: date | str | None) -> date | None:
        if valor is None or valor == "":
            return None
        if isinstance(valor, date) and not isinstance(valor, str):
            return valor
        return date.fromisoformat(str(valor))

    @staticmethod
    def _converter_hora(valor: time | str | None) -> time | None:
        if valor is None or valor == "":
            return None
        if isinstance(valor, time):
            return valor
        return time.fromisoformat(str(valor))

    def validar(self) -> "Pedido":
        campos_obrigatorios = {
            "data_sessao": self.data_sessao,
            "hora_inicio": self.hora_inicio,
            "hora_fim": self.hora_fim,
            "localizacao": self.localizacao,
            "id_cliente": self.id_cliente,
            "id_tipo": self.id_tipo,
        }

        for nome, valor in campos_obrigatorios.items():
            if valor in (None, ""):
                raise ValueError(f"O campo '{nome}' é obrigatório.")

        if not self.codigo_consulta or not self.codigo_consulta.strip():
            self.codigo_consulta = gerar_codigo_consulta()

        if self.hora_inicio >= self.hora_fim:
            raise ValueError("A hora de início deve ser anterior à hora de fim.")

        if self.duracao <= 0:
            raise ValueError("A duração deve ser maior que zero.")

        if self.estado not in ESTADOS_PEDIDO:
            raise ValueError(
                f"Estado inválido '{self.estado}'. Estados válidos: {sorted(ESTADOS_PEDIDO)}"
            )

        self.localizacao = self.localizacao.strip()
        if not self.localizacao:
            raise ValueError("A localização do pedido não pode estar vazia.")

        return self

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "Pedido":
        return cls(**dados)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_pedido": self.id_pedido,
            "codigo_consulta": self.codigo_consulta,
            "data_sessao": self.data_sessao.isoformat() if self.data_sessao else None,
            "hora_inicio": self.hora_inicio.isoformat() if self.hora_inicio else None,
            "hora_fim": self.hora_fim.isoformat() if self.hora_fim else None,
            "localizacao": self.localizacao,
            "duracao": self.duracao,
            "estado": self.estado,
            "observacoes": self.observacoes,
            "id_cliente": self.id_cliente,
            "id_tipo": self.id_tipo,
        }
