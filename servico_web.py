"""Camada de API HTTP local para o front-end Zyra.

Não contém SQL e não substitui o menu do terminal: a API reutiliza
RepositorioOracle e as mesmas validações de negócio das Sprints anteriores.
"""

from contextlib import contextmanager
from threading import Lock

from api_clima import CatalogoClima, ErroAPI
from banco import conectar
from constantes import BONUS_CADASTRO, PONTOS_POR_PASSAGEM, TIPOS_PASSAGEM, VALOR_PASSAGEM
from relatorios import calcular_resumo
from repositorio import ErroBanco, RepositorioOracle


class ErroRequisicao(Exception):
    """Representa uma resposta HTTP esperada, sem vazar detalhes técnicos."""

    def __init__(self, status, mensagem):
        super().__init__(mensagem)
        self.status = status


@contextmanager
def acesso_oracle():
    """Abre e fecha uma conexão independente a cada requisição HTTP."""
    try:
        conexao = conectar()
    except Exception as erro:
        raise ErroBanco("Não foi possível conectar ao Oracle.") from erro
    try:
        yield RepositorioOracle(conexao)
    finally:
        conexao.close()


class ServicoZyra:
    """Regras de endpoints independentes de sockets, permitindo testes locais."""

    def __init__(self, repositorio_factory=None, catalogo_clima=None):
        self._repositorio_factory = repositorio_factory or acesso_oracle
        self._clima = catalogo_clima or CatalogoClima()
        self._clima_lock = Lock()

    @staticmethod
    def _id(texto):
        if not texto.isascii() or not texto.isdecimal() or int(texto) < 1:
            raise ErroRequisicao(404, "Recurso não encontrado.")
        return int(texto)

    @staticmethod
    def _objeto(dados, *campos):
        if not isinstance(dados, dict) or set(dados) != set(campos):
            raise ErroRequisicao(400, "Envie um objeto JSON apenas com: " + ", ".join(campos) + ".")
        return dados

    @staticmethod
    def _usuario(repo, id_usuario):
        usuario = repo.consultar_usuario(id_usuario)
        if usuario is None:
            raise ErroRequisicao(404, "Usuário não encontrado.")
        return usuario

    def processar(self, metodo, rota, dados=None):
        """Retorna (codigo_HTTP, resposta_JSON) sem iniciar o servidor."""
        partes = [p for p in rota.split("/") if p]
        if partes == ["api", "status"] and metodo == "GET":
            return 200, {"status": "ok", "servico": "Zyra API local"}
        if partes == ["api", "passagens"] and metodo == "GET":
            return 200, {
                "pontos_por_passagem": PONTOS_POR_PASSAGEM,
                "valor_passagem_reais": VALOR_PASSAGEM,
                "passagens": [
                    {"tipo": indice, "nome": nome, "viagens": viagens, "custo_pontos": custo}
                    for indice, (nome, viagens, custo) in enumerate(TIPOS_PASSAGEM, start=1)
                ],
            }
        if partes == ["api", "clima"] and metodo == "GET":
            with self._clima_lock:
                try:
                    return 200, self._clima.obter()
                except ErroAPI as erro:
                    raise ErroRequisicao(502, str(erro)) from erro

        if len(partes) < 2 or partes[:1] != ["api"]:
            raise ErroRequisicao(404, "Rota não encontrada.")

        try:
            with self._repositorio_factory() as repo:
                if partes == ["api", "resumo"] and metodo == "GET":
                    return 200, calcular_resumo(repo.listar_usuarios())

                if partes == ["api", "usuarios"]:
                    if metodo == "GET":
                        return 200, {"usuarios": repo.listar_usuarios()}
                    if metodo == "POST":
                        entrada = self._objeto(dados, "nome")
                        id_usuario = repo.criar_usuario(entrada["nome"])
                        return 201, {"usuario": self._usuario(repo, id_usuario), "bonus_cadastro": BONUS_CADASTRO}

                if len(partes) >= 3 and partes[:2] == ["api", "usuarios"]:
                    id_usuario = self._id(partes[2])
                    if len(partes) == 3:
                        if metodo == "GET":
                            return 200, {"usuario": self._usuario(repo, id_usuario)}
                        if metodo == "PATCH":
                            if not isinstance(dados, dict) or len(dados) != 1 or not (set(dados) <= {"nome", "pontos"}):
                                raise ErroRequisicao(400, "Altere apenas 'nome' ou 'pontos' por requisição.")
                            if "nome" in dados:
                                alterou = repo.alterar_nome(id_usuario, dados["nome"])
                            else:
                                alterou = repo.alterar_pontos(id_usuario, dados["pontos"])
                            if not alterou:
                                raise ErroRequisicao(404, "Usuário não encontrado.")
                            return 200, {"usuario": self._usuario(repo, id_usuario)}
                        if metodo == "DELETE":
                            if not repo.excluir_usuario(id_usuario):
                                raise ErroRequisicao(404, "Usuário não encontrado.")
                            return 200, {"excluido": True, "id": id_usuario}

                    if len(partes) == 4 and metodo == "POST":
                        if partes[3] == "pontos":
                            entrada = self._objeto(dados, "quantidade")
                            saldo = repo.adicionar_pontos(id_usuario, entrada["quantidade"])
                            if saldo is None:
                                raise ErroRequisicao(404, "Usuário não encontrado.")
                            return 200, {"usuario": self._usuario(repo, id_usuario)}
                        if partes[3] == "resgates":
                            entrada = self._objeto(dados, "tipo")
                            tipo = entrada["tipo"]
                            if type(tipo) is not int or not 1 <= tipo <= len(TIPOS_PASSAGEM):
                                raise ErroRequisicao(400, "Informe um tipo válido entre 1 e 3.")
                            sucesso, saldo = repo.resgatar_passagem(id_usuario, tipo - 1)
                            if saldo is None:
                                raise ErroRequisicao(404, "Usuário não encontrado.")
                            if not sucesso:
                                raise ErroRequisicao(409, "Saldo insuficiente para resgatar a passagem.")
                            return 201, {"usuario": self._usuario(repo, id_usuario)}

            # Rota reconhecível, mas com método incorreto.
            raise ErroRequisicao(404, "Rota não encontrada.")
        except ValueError as erro:
            raise ErroRequisicao(400, str(erro)) from erro
        except ErroBanco as erro:
            raise ErroRequisicao(503, "Erro ao consultar o Oracle. Verifique a conexão.") from erro
        except (OSError, ConnectionError) as erro:
            raise ErroRequisicao(503, "Conexão com o Oracle indisponível.") from erro
