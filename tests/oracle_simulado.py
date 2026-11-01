"""Adaptador SQLite exclusivo para testes de contratos SQL do repositório.

Não emula o Oracle completo, apenas traduz RETURNING ... INTO para SQLite.
Os testes com Oracle real precisam ser executados pelo aluno na FIAP.
"""

import re
import sqlite3
from decimal import Decimal

sqlite3.register_adapter(Decimal, float)


class Variavel:
    def __init__(self):
        self.valores = []

    def getvalue(self):
        return self.valores


class CursorSimulado:
    def __init__(self, conexao):
        self.conexao = conexao
        self.cursor = conexao.db.cursor()
        self.rowcount = -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()

    def var(self, tipo):
        return Variavel()

    def execute(self, sql, parametros=None):
        if self.conexao.falha_na_troca and "INSERT INTO ZYRA_TROCAS" in sql:
            raise RuntimeError("Falha simulada no insert de trocas")
        parametros = parametros or {}
        retorno = re.search(r"RETURNING\s+(\w+)\s+INTO\s+:(\w+)", sql, flags=re.I)
        if retorno:
            coluna, chave = retorno.groups()
            variavel = parametros[chave]
            parametros = {c: v for c, v in parametros.items() if c != chave}
            sql = sql[:retorno.start()] + f"RETURNING {coluna}" + sql[retorno.end():]
        self.cursor.execute(sql, parametros)
        self.rowcount = self.cursor.rowcount
        if retorno:
            linhas = self.cursor.fetchall()
            variavel.valores = [linha[0] for linha in linhas]
        return self

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()


class ConexaoSimulada:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""
            CREATE TABLE ZYRA_USUARIOS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NOME TEXT NOT NULL, PONTOS INTEGER NOT NULL CHECK(PONTOS >= 0)
            );
            CREATE TABLE ZYRA_TROCAS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USUARIO_ID INTEGER NOT NULL,
                PASSAGEM TEXT NOT NULL,
                VIAGENS INTEGER NOT NULL,
                CUSTO_PONTOS INTEGER NOT NULL,
                VALOR_REAIS NUMERIC NOT NULL
            );
        """)
        self.falha_na_troca = False
        self.commits = 0
        self.rollbacks = 0
        self.fechada = False

    def cursor(self):
        return CursorSimulado(self)

    def commit(self):
        self.db.commit()
        self.commits += 1

    def rollback(self):
        self.db.rollback()
        self.rollbacks += 1

    def close(self):
        self.db.close()
        self.fechada = True
