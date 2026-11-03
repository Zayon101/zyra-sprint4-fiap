"""Criação idempotente e diagnóstico da estrutura Oracle usada pelo Zyra.

O diagnóstico é somente leitura e NÃO corrige automaticamente tabelas
incompatíveis; isso evita alterações perigosas nos dados do professor.
"""

import re
from pathlib import Path

ARQUIVO_SQL = Path(__file__).with_name("criar_tabelas.sql")
TABELAS = ("ZYRA_USUARIOS", "ZYRA_TROCAS")

# Tipo, precisão, escala, comprimento em caracteres, permite nulos.
COLUNAS = {
    "ZYRA_USUARIOS": {
        "ID": ("NUMBER", 10, 0, None, False),
        "NOME": ("VARCHAR2", None, None, 120, False),
        "PONTOS": ("NUMBER", 12, 0, None, False),
    },
    "ZYRA_TROCAS": {
        "ID": ("NUMBER", 10, 0, None, False),
        "USUARIO_ID": ("NUMBER", 10, 0, None, False),
        "PASSAGEM": ("VARCHAR2", None, None, 80, False),
        "VIAGENS": ("NUMBER", 8, 0, None, False),
        "CUSTO_PONTOS": ("NUMBER", 12, 0, None, False),
        "VALOR_REAIS": ("NUMBER", 12, 2, None, False),
        "DATA_TROCA": ("TIMESTAMP", None, None, None, False),
    },
}

CHECAGENS = {
    "ZYRA_USUARIOS": {"CK_ZYRA_USUARIOS_NOME", "CK_ZYRA_USUARIOS_PONTOS"},
    "ZYRA_TROCAS": {"CK_ZYRA_TROCAS_VIAGENS", "CK_ZYRA_TROCAS_CUSTO", "CK_ZYRA_TROCAS_VALOR"},
}


def situacao_tabelas(conexao) -> dict[str, bool]:
    """Verifica a existência das tabelas no esquema do usuário conectado."""
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME FROM USER_TABLES "
            "WHERE TABLE_NAME IN ('ZYRA_USUARIOS', 'ZYRA_TROCAS')"
        )
        existentes = {linha[0] for linha in cursor.fetchall()}
    return {tabela: tabela in existentes for tabela in TABELAS}


def verificar_estrutura(conexao) -> dict[str, list[str]]:
    """Diagnostica colunas, tipos, nulidade, defaults, chaves e índice.

    Retorna uma lista de problemas por objeto. Listas vazias indicam que
    os objetos são compatíveis com o SQL da Sprint 4. Nenhum DDL é executado.
    """
    situacao = situacao_tabelas(conexao)
    problemas: dict[str, list[str]] = {tabela: [] for tabela in TABELAS}
    problemas["IX_ZYRA_TROCAS_USUARIO"] = []

    with conexao.cursor() as cursor:
        for tabela, esperado in COLUNAS.items():
            if not situacao[tabela]:
                problemas[tabela].append("Tabela não encontrada.")
                continue
            cursor.execute(
                "SELECT COLUMN_NAME, DATA_TYPE, DATA_PRECISION, DATA_SCALE, "
                "CHAR_LENGTH, CHAR_USED, NULLABLE FROM USER_TAB_COLUMNS "
                "WHERE TABLE_NAME = :tabela",
                {"tabela": tabela},
            )
            encontradas = {linha[0]: linha[1:] for linha in cursor.fetchall()}
            for nome, (tipo, precisao, escala, comprimento, permite_nulo) in esperado.items():
                if nome not in encontradas:
                    problemas[tabela].append(f"Coluna {nome} não encontrada.")
                    continue
                tipo_atual, prec_atual, escala_atual, comp_atual, unidade, nulo_atual = encontradas[nome]
                # USER_TAB_COLUMNS retorna TIMESTAMP(6) para TIMESTAMP sem escala explícita.
                tipo_valido = (
                    str(tipo_atual).upper().startswith("TIMESTAMP(")
                    if tipo == "TIMESTAMP" else tipo_atual == tipo
                )
                if not tipo_valido:
                    problemas[tabela].append(f"{nome}: tipo {tipo_atual}, esperado {tipo}.")
                if precisao is not None and (prec_atual, escala_atual) != (precisao, escala):
                    problemas[tabela].append(
                        f"{nome}: precisão/escala {prec_atual},{escala_atual}; esperado {precisao},{escala}."
                    )
                if comprimento is not None and (comp_atual != comprimento or unidade != "C"):
                    problemas[tabela].append(
                        f"{nome}: esperado VARCHAR2({comprimento} CHAR)."
                    )
                if (nulo_atual == "Y") != permite_nulo:
                    problemas[tabela].append(f"{nome}: restrição NOT NULL incompatível.")

            # As colunas ID devem ser geradas automaticamente por IDENTITY.
            cursor.execute(
                "SELECT COLUMN_NAME FROM USER_TAB_IDENTITY_COLS WHERE TABLE_NAME = :tabela",
                {"tabela": tabela},
            )
            identidade = {linha[0] for linha in cursor.fetchall()}
            if "ID" not in identidade:
                problemas[tabela].append("ID: coluna IDENTITY não configurada.")

            cursor.execute(
                "SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE, DELETE_RULE, R_CONSTRAINT_NAME, STATUS "
                "FROM USER_CONSTRAINTS WHERE TABLE_NAME = :tabela",
                {"tabela": tabela},
            )
            restricoes = {
                nome: {"tipo": ct, "delete": regra, "referencia": referencia, "status": status}
                for nome, ct, regra, referencia, status in cursor.fetchall()
            }
            cursor.execute(
                "SELECT CONSTRAINT_NAME, COLUMN_NAME, POSITION FROM USER_CONS_COLUMNS "
                "WHERE TABLE_NAME = :tabela ORDER BY CONSTRAINT_NAME, POSITION",
                {"tabela": tabela},
            )
            colunas_restricao: dict[str, list[str]] = {}
            for nome, coluna, _ in cursor.fetchall():
                colunas_restricao.setdefault(nome, []).append(coluna)
            pk = "PK_ZYRA_USUARIOS" if tabela == "ZYRA_USUARIOS" else "PK_ZYRA_TROCAS"
            if (pk not in restricoes or restricoes[pk]["tipo"] != "P"
                    or restricoes[pk]["status"] != "ENABLED"
                    or colunas_restricao.get(pk) != ["ID"]):
                problemas[tabela].append(f"Chave primária {pk} em ID ausente ou incorreta.")
            for nome in CHECAGENS[tabela]:
                if (nome not in restricoes or restricoes[nome]["tipo"] != "C"
                        or restricoes[nome]["status"] != "ENABLED"):
                    problemas[tabela].append(f"Restrição {nome} ausente ou desabilitada.")
            if tabela == "ZYRA_TROCAS":
                fk = restricoes.get("FK_ZYRA_TROCAS_USUARIO", {})
                if (fk.get("tipo") != "R" or fk.get("status") != "ENABLED"
                        or fk.get("referencia") != "PK_ZYRA_USUARIOS"
                        or fk.get("delete") != "CASCADE"
                        or colunas_restricao.get("FK_ZYRA_TROCAS_USUARIO") != ["USUARIO_ID"]):
                    problemas[tabela].append("Chave estrangeira USUARIO_ID com ON DELETE CASCADE incorreta.")

            # Conferir os valores padrão usados em cadastros e histórico.
            padroes = {"PONTOS": "500"} if tabela == "ZYRA_USUARIOS" else {"DATA_TROCA": "SYSTIMESTAMP"}
            cursor.execute(
                "SELECT COLUMN_NAME, DATA_DEFAULT FROM USER_TAB_COLUMNS "
                "WHERE TABLE_NAME = :tabela AND COLUMN_NAME IN ('PONTOS', 'DATA_TROCA')",
                {"tabela": tabela},
            )
            defaults = {nome: str(valor or "").strip().upper() for nome, valor in cursor.fetchall()}
            for nome, valor in padroes.items():
                if defaults.get(nome, "").strip("() ") != valor:
                    problemas[tabela].append(f"{nome}: valor DEFAULT esperado {valor}.")

        if not situacao["ZYRA_TROCAS"]:
            problemas["IX_ZYRA_TROCAS_USUARIO"].append("A tabela de trocas não existe.")
        else:
            cursor.execute(
                "SELECT COLUMN_NAME FROM USER_IND_COLUMNS "
                "WHERE TABLE_NAME = 'ZYRA_TROCAS' AND INDEX_NAME = 'IX_ZYRA_TROCAS_USUARIO' "
                "ORDER BY COLUMN_POSITION"
            )
            if [linha[0] for linha in cursor.fetchall()] != ["USUARIO_ID"]:
                problemas["IX_ZYRA_TROCAS_USUARIO"].append(
                    "Índice IX_ZYRA_TROCAS_USUARIO ausente ou com colunas diferentes."
                )
    return problemas


def instrucoes_criacao(caminho: Path = ARQUIVO_SQL) -> list[tuple[str, str, str]]:
    """Analisa o SQL conhecido e recusa comandos que não sejam CREATE permitido."""
    texto = Path(caminho).read_text(encoding="utf-8")
    sem_comentarios = "\n".join(
        linha for linha in texto.splitlines()
        if not linha.lstrip().startswith("--")
    )
    instrucoes = []
    for bloco in sem_comentarios.split(";"):
        sql = bloco.strip()
        if not sql:
            continue
        correspondencia = re.match(
            r"^CREATE\s+(TABLE|INDEX)\s+([A-Z][A-Z0-9_]*)\b",
            sql, re.IGNORECASE,
        )
        if correspondencia is None:
            raise ValueError("O script contém uma instrução SQL não permitida.")
        tipo, nome = correspondencia.groups()
        instrucoes.append((tipo.upper(), nome.upper(), sql))
    if not instrucoes:
        raise ValueError("O arquivo SQL não possui instruções de criação.")
    return instrucoes


def preparar_estrutura(conexao) -> list[str]:
    """Cria somente tabelas e índices que ainda não existem, sem alterar dados."""
    instrucoes = instrucoes_criacao()
    criados = []
    with conexao.cursor() as cursor:
        for tipo, nome, sql in instrucoes:
            cursor.execute(
                "SELECT 1 FROM USER_OBJECTS "
                "WHERE OBJECT_TYPE = :tipo AND OBJECT_NAME = :nome",
                {"tipo": tipo, "nome": nome},
            )
            if cursor.fetchone() is not None:
                print(f"[OK] {nome} já existe; nada foi alterado.")
                continue
            cursor.execute(sql)
            print(f"[CRIADO] {tipo}: {nome}")
            criados.append(nome)
    return criados
