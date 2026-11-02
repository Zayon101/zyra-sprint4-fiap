"""Cria as tabelas do Zyra, se não existirem, sem apagar dados."""

import re
from contextlib import closing
from pathlib import Path

from zyra.database.banco import conectar


ARQUIVO_SQL = Path(__file__).resolve().parents[1] / "sql" / "criar_tabelas.sql"

# Este script executa apenas estas instruções DDL conhecidas.
TIPOS_PERMITIDOS = {"TABLE": "TABLE", "INDEX": "INDEX"}


def ler_instrucoes_sql(caminho=ARQUIVO_SQL):
    """Lê instruções CREATE TABLE / CREATE INDEX de um arquivo SQL simples."""
    texto = Path(caminho).read_text(encoding="utf-8")
    # O arquivo não contém blocos PL/SQL, strings com ';' nem comandos SQL*Plus.
    linhas = [linha for linha in texto.splitlines() if not linha.lstrip().startswith("--")]
    instrucoes = []

    for fragmento in "\n".join(linhas).split(";"):
        sql = fragmento.strip()
        if not sql:
            continue
        padrao = r"^CREATE\s+(TABLE|INDEX)\s+([A-Z][A-Z0-9_]*)\b"
        identificacao = re.match(padrao, sql, flags=re.IGNORECASE)
        if identificacao is None:
            raise ValueError("O arquivo SQL possui uma instrução não permitida.")
        tipo, nome = identificacao.groups()
        instrucoes.append((TIPOS_PERMITIDOS[tipo.upper()], nome.upper(), sql))

    if not instrucoes:
        raise ValueError("Nenhuma instrução SQL encontrada.")
    return instrucoes


def objeto_existe(cursor, tipo, nome):
    """Verifica se uma tabela ou índice já existe no esquema conectado."""
    cursor.execute(
        "SELECT 1 FROM USER_OBJECTS "
        "WHERE OBJECT_TYPE = :tipo AND OBJECT_NAME = :nome",
        tipo=tipo,
        nome=nome,
    )
    return cursor.fetchone() is not None


def preparar_estrutura(conexao, instrucoes=None):
    """Cria objetos faltantes e retorna os nomes dos que foram criados."""
    if instrucoes is None:
        instrucoes = ler_instrucoes_sql()

    criados = []
    with conexao.cursor() as cursor:
        for tipo, nome, sql in instrucoes:
            if objeto_existe(cursor, tipo, nome):
                print(f"[OK] {nome} já existe. Nenhum dado alterado.")
                continue
            cursor.execute(sql)
            print(f"[CRIADO] {tipo}: {nome}")
            criados.append(nome)

    # Oracle confirma DDL implicitamente. Não é preciso usar commit() aqui.
    return criados


def main():
    """Conecta ao Oracle e prepara as estruturas, com erros amigáveis."""
    try:
        # Valida o SQL antes de abrir a conexão.
        instrucoes = ler_instrucoes_sql()
        with closing(conectar()) as conexao:
            print("Conexão com Oracle estabelecida.")
            preparar_estrutura(conexao, instrucoes)
        print("\nEstrutura da Etapa 2 preparada com sucesso!")
    except (OSError, ValueError, ImportError) as erro:
        print(f"\nNão foi possível preparar o banco: {erro}")
        return 1
    except Exception as erro:
        # No comando de terminal, capturamos também os erros do driver Oracle.
        print(f"\nErro ao acessar o Oracle: {erro}")
        print("Confira o acesso à rede, credenciais e permissões CREATE TABLE/INDEX.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
