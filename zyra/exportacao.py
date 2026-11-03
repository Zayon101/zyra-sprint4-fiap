"""Exporta resultados de SELECT no Oracle para arquivos JSON locais.

Não altera o banco. Cada exportação usa um nome exclusivo e é criada
na pasta exportacoes/ ao lado do programa, independentemente do cwd.
"""

import json
from datetime import datetime
from pathlib import Path

from zyra.core.relatorios import calcular_resumo
from zyra.database.repositorio import RepositorioOracle


PASTA_EXPORTACOES = Path(__file__).resolve().parents[1] / "exportacoes"
TIPOS_EXPORTACAO = ("usuarios", "usuario", "historico", "resumo")


def montar_consulta(repositorio: RepositorioOracle, tipo: str, id_usuario: int | None = None) -> dict | None:
    """Consulta o Oracle e monta o documento a exportar.

    Retorna None para um ID inexistente, evitando gerar arquivo enganoso.
    Para listas vazias, gera um documento JSON válido com a lista vazia.
    """
    if tipo not in TIPOS_EXPORTACAO:
        raise ValueError("Tipo de exportação inválido.")

    if tipo in ("usuarios", "resumo"):
        usuarios = repositorio.listar_usuarios()
        if tipo == "usuarios":
            return {"tipo": tipo, "total": len(usuarios), "usuarios": usuarios}
        return {"tipo": tipo, "resumo": calcular_resumo(usuarios)}

    if type(id_usuario) is not int or id_usuario <= 0:
        raise ValueError("Informe um ID de usuário válido.")

    usuario = repositorio.consultar_usuario(id_usuario)
    if usuario is None:
        return None

    if tipo == "usuario":
        return {"tipo": tipo, "usuario": usuario}

    return {
        "tipo": tipo,
        "usuario": {"id": usuario["id"], "nome": usuario["nome"]},
        "total_trocas": len(usuario["historico"]),
        "trocas": usuario["historico"],
    }


def _nome_arquivo(tipo, id_usuario=None):
    """Gera nome com microssegundos para reduzir colisões de nomes."""
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    referencia = f"_{id_usuario}" if tipo in ("usuario", "historico") else ""
    return f"zyra_{tipo}{referencia}_{momento}.json"


def exportar_consulta(
    repositorio: RepositorioOracle, tipo: str, id_usuario: int | None = None,
    pasta_destino: Path | None = None,
) -> Path | None:
    """Executa SELECT e grava o JSON; retorna Path, ou None para ID ausente.

    Usa 'x' (criação exclusiva) para nunca sobrescrever um arquivo anterior.
    Se a serialização ou escrita falhar, remove apenas o arquivo incompleto.
    A exceção é propagada para que a interface mostre o erro ao usuário.
    """
    documento = montar_consulta(repositorio, tipo, id_usuario)
    if documento is None:
        return None

    pasta = Path(pasta_destino) if pasta_destino is not None else PASTA_EXPORTACOES
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / _nome_arquivo(tipo, id_usuario)
    documento["exportado_em"] = datetime.now().astimezone().isoformat(timespec="seconds")

    criado = False
    try:
        with caminho.open("x", encoding="utf-8") as arquivo:
            criado = True
            json.dump(documento, arquivo, ensure_ascii=False, indent=4, allow_nan=False)
            arquivo.write("\n")
    except (OSError, TypeError, ValueError):
        if criado:
            try:
                caminho.unlink(missing_ok=True)
            except OSError:
                pass
        raise

    return caminho
