"""Importação opcional do JSON da Sprint 3 para tabelas vazias do Oracle.

Os IDs antigos são associados a novos IDs de identidade Oracle, preservando
os usuários e seus históricos, sem sobrescrever outros registros no banco.
"""

import json
from decimal import Decimal, InvalidOperation

from zyra.database.banco import conectar
from zyra.core.constantes import ARQUIVO_DADOS
from zyra.database.repositorio import ErroBanco, RepositorioOracle


def validar_arquivo_json(caminho):
    """Lê e valida a estrutura antiga antes de executar qualquer INSERT."""
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, list):
        raise ValueError("O arquivo JSON deve conter uma lista de usuários.")

    ids = set()
    for indice, usuario in enumerate(dados, 1):
        if not isinstance(usuario, dict):
            raise ValueError(f"Cadastro {indice} não é um objeto JSON.")
        id_antigo = usuario.get("id")
        nome = usuario.get("nome")
        pontos = usuario.get("pontos")
        historico = usuario.get("historico")
        if type(id_antigo) is not int or id_antigo < 1 or id_antigo in ids:
            raise ValueError(f"Cadastro {indice} possui ID inválido ou repetido.")
        ids.add(id_antigo)
        if not isinstance(nome, str) or not 3 <= len(nome.strip()) <= 120:
            raise ValueError(f"Cadastro {indice} possui nome inválido.")
        if type(pontos) is not int or not 0 <= pontos <= 999999999999:
            raise ValueError(f"Cadastro {indice} possui saldo inválido.")
        if not isinstance(historico, list):
            raise ValueError(f"Cadastro {indice} possui histórico inválido.")
        for troca in historico:
            if not isinstance(troca, dict):
                raise ValueError(f"Histórico de {nome} possui registro inválido.")
            passagem = troca.get("passagem")
            viagens = troca.get("viagens")
            custo = troca.get("custo")
            try:
                valor = Decimal(str(troca.get("valor")))
            except InvalidOperation as erro:
                raise ValueError(f"Histórico de {nome} possui valor inválido.") from erro
            if (not isinstance(passagem, str) or not 1 <= len(passagem) <= 80
                or type(viagens) is not int or viagens <= 0
                or type(custo) is not int or custo <= 0
                or not valor.is_finite() or valor < 0):
                raise ValueError(f"Histórico de {nome} possui dados inválidos.")
    return dados


def importar_no_oracle(repositorio, usuarios):
    """Insere cadastros e trocas numa única transação, somente em base vazia."""
    if repositorio.listar_usuarios():
        raise ValueError(
            "Importação cancelada: já existem usuários no Oracle. "
            "Não serão criados cadastros duplicados."
        )
    conexao = repositorio.conexao
    ids_convertidos = {}
    try:
        with conexao.cursor() as cursor:
            for usuario in usuarios:
                novo_id = cursor.var(int)
                cursor.execute(
                    """INSERT INTO ZYRA_USUARIOS (NOME, PONTOS)
                       VALUES (:nome, :pontos) RETURNING ID INTO :novo_id""",
                    {"nome": usuario["nome"].strip(),
                     "pontos": usuario["pontos"], "novo_id": novo_id},
                )
                id_gerado = int(novo_id.getvalue()[0])
                ids_convertidos[usuario["id"]] = id_gerado
                for troca in usuario["historico"]:
                    cursor.execute(
                        """INSERT INTO ZYRA_TROCAS
                           (USUARIO_ID, PASSAGEM, VIAGENS, CUSTO_PONTOS, VALOR_REAIS)
                           VALUES (:id, :passagem, :viagens, :custo, :valor)""",
                        {"id": id_gerado, "passagem": troca["passagem"],
                         "viagens": troca["viagens"], "custo": troca["custo"],
                         "valor": Decimal(str(troca["valor"]))},
                    )
        conexao.commit()
        return ids_convertidos
    except Exception as erro:
        conexao.rollback()
        raise ErroBanco("Falha ao importar o JSON; nenhuma alteração foi salva.") from erro


def main():
    """Importa dados apenas mediante confirmação explícita no terminal."""
    if not ARQUIVO_DADOS.is_file():
        print(f"Arquivo não encontrado: {ARQUIVO_DADOS}")
        print("Se quiser importar, copie seu dados_zyra.json para esta pasta.")
        return
    try:
        usuarios = validar_arquivo_json(ARQUIVO_DADOS)
    except (OSError, ValueError, json.JSONDecodeError) as erro:
        print(f"Não foi possível ler o JSON: {erro}")
        return
    print(f"\nArquivo válido: {len(usuarios)} usuário(s).")
    print("A importação exige tabelas de usuários vazias no Oracle.")
    if input("Digite IMPORTAR para confirmar: ").strip() != "IMPORTAR":
        print("Importação cancelada.")
        return
    try:
        conexao = conectar()
    except Exception as erro:
        print(f"Erro de conexão: {erro}")
        return
    try:
        conversoes = importar_no_oracle(RepositorioOracle(conexao), usuarios)
        print(f"\nImportação finalizada: {len(conversoes)} usuário(s).")
        for antigo, novo in conversoes.items():
            print(f"ID antigo {antigo} -> ID Oracle {novo}")
    except (ValueError, ErroBanco) as erro:
        print(f"Importação não realizada: {erro}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
