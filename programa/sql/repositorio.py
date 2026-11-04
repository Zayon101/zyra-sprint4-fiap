"""Acesso aos usuários e resgates no Oracle, sem interações de terminal.

Todas as consultas usam parâmetros vinculados. Alterações são confirmadas
com commit; em caso de erro, a transação é revertida com rollback.
"""

from datetime import datetime
from decimal import Decimal
import logging

from sistema.modelos import Usuario

from sistema.constantes import BONUS_CADASTRO, MAX_PONTOS, VALOR_PASSAGEM
from sistema.regras import (
    validar_credito, validar_indice_passagem, validar_nome_usuario,
    validar_saldo,
)


logger = logging.getLogger(__name__)


class ErroBanco(RuntimeError):
    """Indica falha em uma operação de persistência Oracle."""


class RepositorioOracle:
    """Concentra as operações SQL do Zyra numa única conexão Oracle."""

    def __init__(self, conexao):
        self.conexao = conexao

    def listar_usuarios(self, incluir_historico: bool = True) -> list[Usuario]:
        """Lista os usuários; permite omitir históricos para telas resumidas.

        Sem argumento mantém a estrutura completa usada pela API e exportação.
        """
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
                if not incluir_historico:
                    return list(usuarios.values())
                cursor.execute(
                    """SELECT ID, USUARIO_ID, PASSAGEM, VIAGENS,
                              CUSTO_PONTOS, VALOR_REAIS, DATA_TROCA
                       FROM ZYRA_TROCAS ORDER BY ID"""
                )
                for id_troca, usuario_id, passagem, viagens, custo, valor, data in cursor.fetchall():
                    usuario = usuarios.get(int(usuario_id))
                    if usuario is not None:
                        usuario["historico"].append({
                            "id": int(id_troca),
                            "data": self._data_iso(data),
                            "passagem": passagem,
                            "viagens": int(viagens),
                            "custo": int(custo),
                            "valor": float(valor),
                        })
                return list(usuarios.values())
        except (TypeError, KeyError, AttributeError) as erro:
            logger.exception("Erro inesperado ao processar dados de usuários.")
            raise
        except Exception as erro:
            raise ErroBanco("Falha ao consultar usuários no Oracle.") from erro

    def possui_usuarios(self) -> bool:
        """Verifica a existência de cadastros sem carregar histórico ou lista."""
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ZYRA_USUARIOS")
                return cursor.fetchone()[0] > 0
        except Exception as erro:
            raise ErroBanco("Falha ao verificar cadastros no Oracle.") from erro

    def consultar_usuario(self, id_usuario: int) -> Usuario | None:
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
                    """SELECT ID, PASSAGEM, VIAGENS, CUSTO_PONTOS,
                              VALOR_REAIS, DATA_TROCA
                       FROM ZYRA_TROCAS WHERE USUARIO_ID = :id ORDER BY ID""",
                    {"id": id_usuario},
                )
                for id_troca, passagem, viagens, custo, valor, data in cursor.fetchall():
                    usuario["historico"].append({
                        "id": int(id_troca),
                        "data": self._data_iso(data),
                        "passagem": passagem,
                        "viagens": int(viagens),
                        "custo": int(custo),
                        "valor": float(valor),
                    })
                return usuario
        except (TypeError, KeyError, AttributeError) as erro:
            logger.exception("Erro inesperado ao processar cadastro do usuário.")
            raise
        except Exception as erro:
            raise ErroBanco("Falha ao consultar usuário no Oracle.") from erro

    @staticmethod
    def _data_iso(data: datetime | str) -> str:
        """Converte data do Oracle para texto ISO facilmente serializável."""
        if isinstance(data, datetime):
            return data.isoformat(timespec="seconds")
        if isinstance(data, str):
            return data.replace(" ", "T")
        raise ValueError("Data de troca inválida retornada pelo banco.")

    def criar_usuario(self, nome: str) -> int:
        """Insere um cadastro com bônus inicial e devolve o ID gerado."""
        nome = validar_nome_usuario(nome)
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
        except (TypeError, AttributeError, KeyError):
            self.conexao.rollback()
            logger.exception("Erro inesperado durante o cadastro.")
            raise
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao cadastrar usuário no Oracle.") from erro

    def alterar_nome(self, id_usuario: int, nome: str) -> bool:
        """Altera o nome e retorna False se o usuário não existir."""
        nome = validar_nome_usuario(nome)
        return self._alterar(
            "UPDATE ZYRA_USUARIOS SET NOME = :nome WHERE ID = :id",
            {"nome": nome, "id": id_usuario},
        )

    def alterar_pontos(self, id_usuario: int, pontos: int) -> bool:
        """Define o saldo de pontos e retorna False para ID inexistente."""
        validar_saldo(pontos)
        return self._alterar(
            "UPDATE ZYRA_USUARIOS SET PONTOS = :pontos WHERE ID = :id",
            {"pontos": pontos, "id": id_usuario},
        )

    def excluir_usuario(self, id_usuario: int) -> bool:
        """Exclui o cadastro pelo ID (Oracle apaga o histórico em cascata)."""
        return self._alterar(
            "DELETE FROM ZYRA_USUARIOS WHERE ID = :id", {"id": id_usuario}
        )

    def _alterar(self, sql: str, parametros: dict) -> bool:
        """Executa uma alteração parametrizada com transação explícita."""
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, parametros)
                alterados = cursor.rowcount
            self.conexao.commit()
            return alterados == 1
        except (TypeError, AttributeError, KeyError):
            self.conexao.rollback()
            logger.exception("Erro inesperado durante alteração SQL.")
            raise
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao alterar dados no Oracle.") from erro

    def adicionar_pontos(self, id_usuario: int, quantidade: int) -> int | None:
        """Soma pontos diretamente no banco, sem sobrescrever um saldo antigo."""
        validar_credito(quantidade)
        try:
            with self.conexao.cursor() as cursor:
                saldo = cursor.var(int)
                cursor.execute(
                    """UPDATE ZYRA_USUARIOS SET PONTOS = PONTOS + :quantidade
                       WHERE ID = :id AND PONTOS <= :limite
                       RETURNING PONTOS INTO :novo_saldo""",
                    {"quantidade": quantidade, "id": id_usuario,
                     "limite": MAX_PONTOS - quantidade, "novo_saldo": saldo},
                )
                valores = saldo.getvalue()
            if not valores:
                self.conexao.rollback()
                # Diferencia limite de pontos de cadastro inexistente.
                usuario = self.consultar_usuario(id_usuario)
                if usuario is not None:
                    raise ValueError("O crédito ultrapassaria o limite de pontos do Oracle.")
                return None
            self.conexao.commit()
            return int(valores[0])
        except ValueError:
            self.conexao.rollback()
            raise
        except (TypeError, AttributeError, KeyError):
            self.conexao.rollback()
            logger.exception("Erro inesperado durante crédito de pontos.")
            raise
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao adicionar pontos no Oracle.") from erro

    def resgatar_passagem(self, id_usuario: int, indice_passagem: int) -> tuple[bool, int | None]:
        """Desconta pontos e registra a troca em uma única transação.

        Retorna (sucesso, saldo_atual). Nenhuma alteração ocorre se o saldo
        for insuficiente. O índice representa a posição em TIPOS_PASSAGEM.
        """
        passagem, viagens, custo = validar_indice_passagem(indice_passagem)
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
        except (TypeError, AttributeError, KeyError):
            self.conexao.rollback()
            logger.exception("Erro inesperado durante resgate de passagem.")
            raise
        except Exception as erro:
            self.conexao.rollback()
            raise ErroBanco("Falha ao registrar o resgate no Oracle.") from erro
