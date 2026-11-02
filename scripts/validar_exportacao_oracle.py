"""Validação da Etapa 5 no Oracle real, sem alterar seus registros.

Os arquivos de teste são gravados numa pasta temporária e removidos
imediatamente após a validação. Não exibe nomes nem dados pessoais.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from zyra.database.banco import conectar
from zyra.exportacao import exportar_consulta
from zyra.database.repositorio import RepositorioOracle


def validar_json(caminho: Path, tipo: str):
    """Verifica se a exportação existe e contém o tipo esperado."""
    with caminho.open("r", encoding="utf-8") as arquivo:
        documento = json.load(arquivo)
    if documento.get("tipo") != tipo or not documento.get("exportado_em"):
        raise AssertionError(f"Conteúdo JSON inválido para {tipo}.")
    return documento


def main():
    """Verifica SELECT + JSON em conexão real e retorna código de saída."""
    print("TESTE DE EXPORTAÇÃO JSON - ORACLE FIAP")
    print("Somente consultas SELECT. Nenhum cadastro será alterado.")
    print("Arquivos temporários serão apagados após o teste.\n")

    try:
        conexao = conectar()
    except Exception as erro:
        print(f"[ERRO] Não foi possível conectar: {erro}")
        return 1

    try:
        repositorio = RepositorioOracle(conexao)
        with TemporaryDirectory(prefix="zyra_teste_json_") as pasta:
            usuarios = validar_json(
                exportar_consulta(repositorio, "usuarios", pasta_destino=pasta), "usuarios"
            )
            if usuarios["total"] != len(usuarios["usuarios"]):
                raise AssertionError("Quantidade de usuários incorreta.")
            print("[OK] SELECT e exportação de todos os usuários")

            resumo = validar_json(
                exportar_consulta(repositorio, "resumo", pasta_destino=pasta), "resumo"
            )
            if resumo["resumo"]["total_usuarios"] != usuarios["total"]:
                raise AssertionError("Resumo divergente da listagem.")
            print("[OK] Exportação do resumo geral")

            if usuarios["usuarios"]:
                id_usuario = usuarios["usuarios"][0]["id"]
                unico = validar_json(
                    exportar_consulta(repositorio, "usuario", id_usuario, pasta), "usuario"
                )
                historico = validar_json(
                    exportar_consulta(repositorio, "historico", id_usuario, pasta), "historico"
                )
                if unico["usuario"]["id"] != id_usuario:
                    raise AssertionError("ID do usuário divergente.")
                if historico["total_trocas"] != len(historico["trocas"]):
                    raise AssertionError("Quantidade de trocas incorreta.")
                print("[OK] Exportação individual por ID")
                print("[OK] Exportação do histórico do usuário")
            else:
                print("[INFO] Sem usuários: exportações individuais não aplicáveis.")

        print("\nEtapa 5 validada no Oracle real! Arquivos temporários removidos.")
        return 0
    except Exception as erro:
        print(f"[ERRO] Falha na validação: {erro}")
        return 1
    finally:
        conexao.close()


if __name__ == "__main__":
    raise SystemExit(main())
