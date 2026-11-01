"""Acesso aos usuários e resgates no Oracle, sem interações de terminal.

Todas as consultas usam parâmetros vinculados. Alterações são confirmadas
com commit; em caso de erro, a transação é revertida com rollback.
"""

from decimal import Decimal

from constantes import BONUS_CADASTRO, TIPOS_PASSAGEM, VALOR_PASSAGEM


class ErroBanco(RuntimeError):
    """Indica falha em uma operação de persistência Oracle."""


class RepositorioOracle:
    """Concentra as operações SQL do Zyra numa única conexão Oracle."""

    def __init__(self, conexao):
        self.conexao = conexao

    def listar_usuarios(self):
        """Consulta usuários e históricos existentes diretamente no Oracle."""
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("SELECT ID, NOME, PONTOS FROM ZYRA_USUARIOS ORDER BY ID")
                usuarios = {
                    int(id_usuario): {
                        "id": int(id_usuario),
                        "nome": nome,
                        "pontos": int(pontos),
                        "historico": [],
                    }
                    for id_usuario, nome, pontos in cursor.fetchall()
                }
                cursor.execute(
                    """SELECT USUARIO_ID, PASSAGEM, VIAGENS, CUSTO_PONTOS, VALOR_REAIS
                       FROM ZYRA_TROCAS ORDER BY ID"""
                )
                for usuario_id, passagem, viagens, custo, valor in cursor.fetchall():
                    usuario = usuarios.get(int(usuario_id))
                    if usuario is not None:
                        usuario["historico"].append({
                            "passagem": passagem,
                            "viagens": int(viagens),
                            "custo": int(custo),
                            "valor": float(valor),
                        })
                return list(usuarios.values())
        except Exception as erro:
            raise ErroBanco("Falha ao consultar usuários no Oracle.") from erro

    def consultar_usuario(self, id_usuario):
        """Consulta o usuário por ID, incluindo seu histórico de resgates."""
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT ID, NOME, PONTOS FROM ZYRA_USUARIOS WHERE ID = :id",
                    {"id": id_usuario},
                )
                linha = cursor.fetchone()
                if linha is None:
                    return None

                usuario = {
                    "id": int(linha[0]),
                    "nome": linha[1],
                    "pontos": int(linha[2]),
                    "historico": [],
                }
                cursor.execute(
                    """SELECT PASSAGEM, VIAGENS, CUSTO_PONTOS, VALOR_REAIS
                       FROM ZYRA_TROCAS WHERE USUARIO_ID = :id ORDER BY ID""",
                    {"id": id_usuario},
                )
                for passagem, viagens, custo, valor in cursor.fetchall():
                    usuario["historico"].append({
                        "passagem": passagem,
                        "viagens": int(viagens),
                        "custo": int(custo),
                        "valor": float(valor),
                    })
                return usuario
        except Exception as erro:
            raise ErroBanco("Falha ao consultar usuário no Oracle.") from erro

    def criar_usuario(self, nome):
        """Insere um cadastro com bônus inicial e devolve o ID gerado."""
        nome = nome.strip()
        if len(nome) < 3:
            raise ValueError("O nome deve ter pelo menos três caracteres.")
        try:
            with self.conexao.cursor() as cursor:
                novo_id = cursor.var(int)
                cursor.execute(
                    """INSERT INTO ZYRA_USUARIOS (NOME, PONTOS)
                       VALUES (:nome, :pontos)
                       RETURNING ID INTO :novo_id""",
                    {"nome": nome, "pontos": BONUS_CADASTRO, "novo_id": novo_id},
                )
                id_criado = int(novo_id.getvalue()[0])
            self.conexao.commit()
            return id_criado
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao cadastrar usuário no Oracle.") from erro

    def alterar_nome(self, id_usuario, nome):
        """Altera o nome e retorna False se o usuário não existir."""
        nome = nome.strip()
        if len(nome) < 3:
            raise ValueError("O nome deve ter pelo menos três caracteres.")
        return self._alterar(
            "UPDATE ZYRA_USUARIOS SET NOME = :nome WHERE ID = :id",
            {"nome": nome, "id": id_usuario},
        )

    def alterar_pontos(self, id_usuario, pontos):
        """Define o saldo de pontos e retorna False para ID inexistente."""
        if type(pontos) is not int or pontos < 0:
            raise ValueError("O saldo deve ser um inteiro não negativo.")
        return self._alterar(
            "UPDATE ZYRA_USUARIOS SET PONTOS = :pontos WHERE ID = :id",
            {"pontos": pontos, "id": id_usuario},
        )

    def excluir_usuario(self, id_usuario):
        """Exclui o cadastro pelo ID (Oracle apaga o histórico em cascata)."""
        return self._alterar(
            "DELETE FROM ZYRA_USUARIOS WHERE ID = :id", {"id": id_usuario}
        )

    def _alterar(self, sql, parametros):
        """Executa uma alteração parametrizada com transação explícita."""
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, parametros)
                alterados = cursor.rowcount
            self.conexao.commit()
            return alterados == 1
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao alterar dados no Oracle.") from erro

    def adicionar_pontos(self, id_usuario, quantidade):
        """Soma pontos diretamente no banco, sem sobrescrever um saldo antigo."""
        if type(quantidade) is not int or quantidade <= 0:
            raise ValueError("A quantidade deve ser um inteiro positivo.")
        try:
            with self.conexao.cursor() as cursor:
                saldo = cursor.var(int)
                cursor.execute(
                    """UPDATE ZYRA_USUARIOS SET PONTOS = PONTOS + :quantidade
                       WHERE ID = :id RETURNING PONTOS INTO :novo_saldo""",
                    {"quantidade": quantidade, "id": id_usuario, "novo_saldo": saldo},
                )
                valores = saldo.getvalue()
            self.conexao.commit()
            return int(valores[0]) if valores else None
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao adicionar pontos no Oracle.") from erro

    def resgatar_passagem(self, id_usuario, indice_passagem):
        """Desconta pontos e registra a troca em uma única transação.

        Retorna (sucesso, saldo_atual). Nenhuma alteração ocorre se o saldo
        for insuficiente. O índice representa a posição em TIPOS_PASSAGEM.
        """
        if not 0 <= indice_passagem < len(TIPOS_PASSAGEM):
            raise ValueError("Tipo de passagem inválido.")
        passagem, viagens, custo = TIPOS_PASSAGEM[indice_passagem]
        try:
            with self.conexao.cursor() as cursor:
                novo_saldo = cursor.var(int)
                cursor.execute(
                    """UPDATE ZYRA_USUARIOS SET PONTOS = PONTOS - :custo
                       WHERE ID = :id AND PONTOS >= :custo_min
                       RETURNING PONTOS INTO :novo_saldo""",
                    {
                        "id": id_usuario, "custo": custo,
                        "custo_min": custo, "novo_saldo": novo_saldo,
                    },
                )
                saldos = novo_saldo.getvalue()
                if not saldos:
                    self.conexao.rollback()
                    usuario = self.consultar_usuario(id_usuario)
                    return False, None if usuario is None else usuario["pontos"]

                cursor.execute(
                    """INSERT INTO ZYRA_TROCAS
                       (USUARIO_ID, PASSAGEM, VIAGENS, CUSTO_PONTOS, VALOR_REAIS)
                       VALUES (:id, :passagem, :viagens, :custo, :valor)""",
                    {
                        "id": id_usuario, "passagem": passagem,
                        "viagens": viagens, "custo": custo,
                        "valor": Decimal(str(VALOR_PASSAGEM)) * viagens,
                    },
                )
                saldo_final = int(saldos[0])
            self.conexao.commit()
            return True, saldo_final
        except ErroBanco:
            raise
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao registrar o resgate no Oracle.") from erro
