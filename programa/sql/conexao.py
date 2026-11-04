"""Conexão Oracle e armazenamento *opcional* de credenciais locais.

O armazenamento é feito em JSON, com senha em texto simples, somente após
consentimento explícito. Não compartilhe o arquivo com terceiros ou no Git.
"""

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

ARQUIVO_CONEXAO = Path(__file__).resolve().parent.parent / "sistema" / "conexao_oracle.local.json"


@dataclass(frozen=True)
class ConfiguracaoBanco:
    """Parâmetros de conexão informados pelo operador."""

    usuario: str
    senha: str = field(repr=False)
    host: str = ""
    porta: int = 1521
    servico: str = ""
    sid: str = ""


def salvar_conexao_local(configuracao: ConfiguracaoBanco, caminho: Path = ARQUIVO_CONEXAO) -> None:
    """Grava as credenciais locais sob consentimento, com escrita atômica.

    Atenção: senha armazenada em texto simples; permissões são limitadas
    ao usuário atual quando o sistema operacional oferece esse recurso.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        descritor, temporario = tempfile.mkstemp(prefix=".zyra-oracle-", suffix=".tmp", dir=caminho.parent)
        with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
            json.dump(asdict(configuracao), arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        os.replace(temporario, caminho)
    finally:
        if temporario is not None:
            Path(temporario).unlink(missing_ok=True)


def carregar_conexao_local(caminho: Path = ARQUIVO_CONEXAO) -> ConfiguracaoBanco | None:
    """Retorna uma configuração salva, ou None caso não haja arquivo."""
    caminho = Path(caminho)
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, json.JSONDecodeError) as erro:
        raise ValueError("O arquivo de conexão salvo não pôde ser lido.") from erro
    if not isinstance(dados, dict):
        raise ValueError("O arquivo de conexão salvo possui formato inválido.")
    chaves = {"usuario", "senha", "host", "porta", "servico", "sid"}
    if set(dados) != chaves:
        raise ValueError("O arquivo de conexão salvo está incompleto ou inválido.")
    if (not all(isinstance(dados[campo], str) for campo in chaves - {"porta"})
            or type(dados["porta"]) is not int):
        raise ValueError("O arquivo de conexão salvo possui campos inválidos.")
    configuracao = ConfiguracaoBanco(**dados)
    if (not configuracao.usuario.strip() or not configuracao.senha or not configuracao.host.strip()
            or bool(configuracao.sid) == bool(configuracao.servico)
            or not 1 <= configuracao.porta <= 65535):
        raise ValueError("O arquivo de conexão salvo possui parâmetros inválidos.")
    return configuracao


def excluir_conexao_local(caminho: Path = ARQUIVO_CONEXAO) -> bool:
    """Apaga o arquivo salvo, se existir (sem encerrar a sessão atual)."""
    try:
        Path(caminho).unlink()
    except FileNotFoundError:
        return False
    return True


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
