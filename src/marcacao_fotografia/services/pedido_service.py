from __future__ import annotations

from typing import Any

from marcacao_fotografia.domain.pedido import Pedido, gerar_codigo_consulta
from marcacao_fotografia.repositories.pedido_repository import PedidoRepository


class PedidoService:
    def __init__(self, repository: PedidoRepository | None = None):
        self.repository = repository or PedidoRepository()

    def criar_pedido(self, **dados: Any) -> Pedido:
        pedido = Pedido.from_dict(dados)
        pedido.validar()

        while self.repository.codigo_consulta_existe(pedido.codigo_consulta):
            pedido.codigo_consulta = gerar_codigo_consulta()

        return self.repository.salvar(pedido)

    def buscar_por_id(self, id_pedido: int) -> Pedido | None:
        return self.repository.buscar_por_id(id_pedido)

    def buscar_por_codigo_consulta(self, codigo_consulta: str) -> Pedido | None:
        return self.repository.buscar_por_codigo_consulta(codigo_consulta)

    def listar_pedidos(self) -> list[Pedido]:
        return self.repository.listar_todos()

    def atualizar_pedido(self, id_pedido: int, **dados: Any) -> Pedido:
        pedido_atual = self.repository.buscar_por_id(id_pedido)
        if pedido_atual is None:
            raise ValueError(f"Pedido com id {id_pedido} não encontrado.")

        for chave, valor in dados.items():
            if hasattr(pedido_atual, chave):
                setattr(pedido_atual, chave, valor)

        pedido_atual.validar()

        if (
            "codigo_consulta" in dados
            and dados["codigo_consulta"] != pedido_atual.codigo_consulta
            and self.repository.codigo_consulta_existe(pedido_atual.codigo_consulta)
        ):
            pedido_atual.codigo_consulta = gerar_codigo_consulta()

        return self.repository.salvar(pedido_atual)

    def remover_pedido(self, id_pedido: int) -> bool:
        return self.repository.remover(id_pedido)

    def salvar_pedido(self, pedido: Pedido) -> Pedido:
        return self.repository.salvar(pedido)

    def buscar_pedido(self, codigo_consulta: str) -> Pedido | None:
        return self.buscar_por_codigo_consulta(codigo_consulta)
