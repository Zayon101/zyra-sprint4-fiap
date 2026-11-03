"""Conexão com Oracle. Credenciais são informadas no menu principal.

O argumento de conectar() é a configuração da sessão atual; nenhuma senha
é gravada no projeto. O modo sem argumento usa variáveis de ambiente, se
algum integrador externo quiser configurar o servidor dessa maneira.
"""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConfiguracaoBanco:
    """Parâmetros de conexão informados pelo operador."""

    usuario: str
    senha: str = field(repr=False)
    host: str = ""
    porta: int = 1521
    servico: str = ""
    sid: str = ""


def carregar_configuracao() -> ConfiguracaoBanco:
    """Alternativa para integrações externas que usam variáveis de ambiente."""
    return ConfiguracaoBanco(
        usuario=os.getenv("ORACLE_USER", "").strip(),
        senha=os.getenv("ORACLE_PASSWORD", ""),
        host=os.getenv("ORACLE_HOST", "").strip(),
        porta=int(os.getenv("ORACLE_PORT", "1521")),
        servico=os.getenv("ORACLE_SERVICE_NAME", "").strip(),
        sid=os.getenv("ORACLE_SID", "").strip(),
    )


def conectar(configuracao: ConfiguracaoBanco | None = None):
    """Conecta ao Oracle (modo Thin), retornando conexão a ser fechada."""
    if configuracao is None:
        configuracao = carregar_configuracao()

    if not configuracao.usuario or not configuracao.senha or not configuracao.host:
        raise ValueError("Informe usuário, senha e host para conectar ao Oracle.")
    if bool(configuracao.servico) == bool(configuracao.sid):
        raise ValueError("Informe somente SID ou somente nome de serviço.")
    if not 1 <= configuracao.porta <= 65535:
        raise ValueError("A porta deve estar entre 1 e 65535.")

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
