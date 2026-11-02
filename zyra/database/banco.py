"""Configuração e conexão com o Oracle da FIAP (Sprint 4)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


PASTA_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO_AMBIENTE = PASTA_PROJETO / ".env"


@dataclass(frozen=True)
class ConfiguracaoBanco:
    """Reúne os parâmetros necessários para estabelecer uma conexão Oracle."""

    usuario: str
    senha: str = field(repr=False)
    host: str = ""
    porta: int = 1521
    servico: str = ""
    sid: str = ""


def carregar_configuracao():
    """Lê as credenciais do ambiente e valida os dados obrigatórios."""
    load_dotenv(ARQUIVO_AMBIENTE, override=False)

    usuario = os.getenv("ORACLE_USER", "").strip()
    senha = os.getenv("ORACLE_PASSWORD", "")
    host = os.getenv("ORACLE_HOST", "").strip()
    porta_texto = os.getenv("ORACLE_PORT", "1521").strip()
    servico = os.getenv("ORACLE_SERVICE_NAME", "").strip()
    sid = os.getenv("ORACLE_SID", "").strip()

    faltando = []
    if not usuario:
        faltando.append("ORACLE_USER")
    if not senha:
        faltando.append("ORACLE_PASSWORD")
    if not host:
        faltando.append("ORACLE_HOST")
    if faltando:
        raise ValueError(
            "Configuração incompleta. Preencha no .env: " + ", ".join(faltando)
        )

    if bool(servico) == bool(sid):
        raise ValueError(
            "Informe exatamente um identificador no .env: "
            "ORACLE_SERVICE_NAME ou ORACLE_SID."
        )

    try:
        porta = int(porta_texto)
    except ValueError as erro:
        raise ValueError("ORACLE_PORT precisa ser um número inteiro.") from erro
    if not 1 <= porta <= 65535:
        raise ValueError("ORACLE_PORT deve estar entre 1 e 65535.")

    return ConfiguracaoBanco(
        usuario=usuario,
        senha=senha,
        host=host,
        porta=porta,
        servico=servico,
        sid=sid,
    )


def conectar(configuracao=None):
    """Abre e retorna uma conexão Oracle usando o driver python-oracledb.

    Utiliza o modo Thin por padrão, sem exigir o Oracle Instant Client.
    O chamador é responsável por encerrar a conexão após o uso.
    """
    if configuracao is None:
        configuracao = carregar_configuracao()

    # Importação sob demanda: configuração pode ser testada sem o driver.
    import oracledb

    parametros = {
        "user": configuracao.usuario,
        "password": configuracao.senha,
        "host": configuracao.host,
        "port": configuracao.porta,
    }
    if configuracao.servico:
        parametros["service_name"] = configuracao.servico
    else:
        parametros["sid"] = configuracao.sid

    return oracledb.connect(**parametros)
