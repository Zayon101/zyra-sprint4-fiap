"""Configurações fixas do Zyra - Sprint 4."""

from pathlib import Path

# O arquivo de dados continua ao lado do código enquanto o banco é preparado.
PASTA_PROGRAMA = Path(__file__).resolve().parent
ARQUIVO_DADOS = PASTA_PROGRAMA / "dados_zyra.json"

BONUS_CADASTRO = 500
VALOR_PASSAGEM = 5.40
PONTOS_POR_PASSAGEM = 587
VALOR_POR_PONTO = VALOR_PASSAGEM / PONTOS_POR_PASSAGEM

# (nome, quantidade de viagens, custo em pontos)
TIPOS_PASSAGEM = (
    ("Unitária", 1, PONTOS_POR_PASSAGEM),
    ("Ida e volta", 2, PONTOS_POR_PASSAGEM * 2),
    ("Pacote com 5 viagens", 5, PONTOS_POR_PASSAGEM * 5),
)
