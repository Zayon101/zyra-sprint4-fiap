"""Estruturas de dados compartilhadas entre Oracle, CLI, API e JSON."""

from typing import TypedDict


class Troca(TypedDict):
    """Uma passagem registrada no histórico de resgates."""

    id: int
    data: str
    passagem: str
    viagens: int
    custo: int
    valor: float


class Usuario(TypedDict):
    """Formato do cadastro devolvido pelas consultas SQL."""

    id: int
    nome: str
    pontos: int
    historico: list[Troca]


class Resumo(TypedDict):
    """Indicadores exibidos no terminal e disponibilizados em JSON."""

    total_usuarios: int
    total_pontos: int
    valor_total_saldo_reais: float
    total_trocas: int
    total_viagens: int
    valor_total_resgatado_reais: float
