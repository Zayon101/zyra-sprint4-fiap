"""Verificação e criação idempotente das tabelas do Zyra no Oracle.

Só executa as instruções CREATE TABLE e CREATE INDEX do SQL do projeto.
Não executa DROP, DELETE, INSERT nem ALTER em tabelas existentes.
"""

import re
from pathlib import Path

ARQUIVO_SQL = Path(__file__).with_name("criar_tabelas.sql")
TABELAS = ("ZYRA_USUARIOS", "ZYRA_TROCAS")


def situacao_tabelas(conexao) -> dict[str, bool]:
    """Consulta o esquema atualmente conectado sem alterar nenhum dado."""
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME FROM USER_TABLES "
            "WHERE TABLE_NAME IN ('ZYRA_USUARIOS', 'ZYRA_TROCAS')"
        )
        existentes = {linha[0] for linha in cursor.fetchall()}
    return {tabela: tabela in existentes for tabela in TABELAS}


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
    """Cria somente tabelas/índices ausentes no usuário Oracle atual."""
    # Analisa todas as instruções antes de executar a primeira.
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
    # CREATE TABLE/INDEX realiza commit implícito no Oracle.
    return criados
