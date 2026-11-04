"""Sessões de identificação demonstrativa da área pessoal (somente loopback).

NÃO autentica pessoas: conhecer o nome ou ID permite escolher qualquer cadastro.
As rotas pessoais trabalham somente com o ID guardado na sessão do servidor.
"""

from secrets import token_urlsafe
from threading import Lock
from time import monotonic
from unicodedata import normalize, combining

from sistema.constantes import MAX_CARACTERES_NOME
from sistema.modelos import Usuario
from api.servico import ErroRequisicao

DURACAO_SESSAO = 3600  # segundos; perde-se a sessão ao reiniciar o servidor
COOKIE_NOME = "zyra_demo"


def _chave_nome(nome: str) -> str:
    """Compara nomes ignorando acentos e diferença de maiúsculas."""
    return "".join(c for c in normalize("NFKD", nome.casefold()) if not combining(c))


class ServicoPessoal:
    """Guarda sessões efêmeras e restringe operações ao usuário selecionado."""

    def __init__(self, servico):
        self._servico = servico
        self._sessoes = {}
        self._lock = Lock()

    @staticmethod
    def _identificador(dados: dict) -> str:
        if not isinstance(dados, dict) or set(dados) != {"identificador"}:
            raise ErroRequisicao(400, "Informe apenas o campo identificador.")
        valor = dados["identificador"]
        if not isinstance(valor, str):
            raise ErroRequisicao(400, "Informe o nome ou ID como texto.")
        valor = valor.strip()
        if not valor or len(valor) > MAX_CARACTERES_NOME:
            raise ErroRequisicao(400, f"Informe um nome ou ID válido (até {MAX_CARACTERES_NOME} caracteres).")
        return valor

    def _id_sessao(self, token: str | None) -> int:
        if not isinstance(token, str) or not token or len(token) > 100:
            raise ErroRequisicao(401, "Identifique-se para acessar sua área pessoal.")
        agora = monotonic()
        with self._lock:
            registro = self._sessoes.get(token)
            if registro is None:
                raise ErroRequisicao(401, "Sessão não encontrada. Identifique-se novamente.")
            id_usuario, expira = registro
            if expira <= agora:
                del self._sessoes[token]
                raise ErroRequisicao(401, "Sessão expirada. Identifique-se novamente.")
            return id_usuario

    def _buscar_usuario(self, identificador: str) -> Usuario:
        if identificador.isascii() and identificador.isdecimal():
            # Não pesquisar por nome quando parece um ID.
            if len(identificador) > 18 or int(identificador) < 1:
                raise ErroRequisicao(404, "Usuário não encontrado.")
            _, dados = self._servico.processar("GET", f"/api/usuarios/{int(identificador)}")
            return dados["usuario"]

        encontrados = [u for u in self._servico.listar_identificadores()
                      if _chave_nome(u["nome"]) == _chave_nome(identificador)]
        if not encontrados:
            raise ErroRequisicao(404, "Usuário não encontrado.")
        if len(encontrados) != 1:
            raise ErroRequisicao(409, "Há usuários com esse nome. Utilize o ID do seu cadastro.")
        _, dados = self._servico.processar("GET", f"/api/usuarios/{encontrados[0]['id']}")
        return dados["usuario"]

    def processar(self, metodo, rota, dados=None, token=None):
        """Retorna status, corpo JSON, e cookie opcional a enviar na resposta."""
        if rota == "/api/pessoal/entrar" and metodo == "POST":
            usuario = self._buscar_usuario(self._identificador(dados))
            novo_token = token_urlsafe(32)
            with self._lock:
                agora = monotonic()
                # Limpeza incremental de sessões expiradas no processo local.
                self._sessoes = {t: sessao for t, sessao in self._sessoes.items() if sessao[1] > agora}
                if token:
                    self._sessoes.pop(token, None)
                self._sessoes[novo_token] = (usuario["id"], agora + DURACAO_SESSAO)
            cookie = f"{COOKIE_NOME}={novo_token}; Path=/api/pessoal; HttpOnly; SameSite=Strict; Max-Age={DURACAO_SESSAO}"
            return 200, {"usuario": usuario, "aviso": "Acesso demonstrativo, sem verificação de identidade."}, cookie

        if rota == "/api/pessoal/sair" and metodo == "POST":
            if token:
                with self._lock:
                    self._sessoes.pop(token, None)
            cookie = f"{COOKIE_NOME}=; Path=/api/pessoal; HttpOnly; SameSite=Strict; Max-Age=0"
            return 200, {"encerrada": True}, cookie

        if rota not in ("/api/pessoal/conta", "/api/pessoal/resgates"):
            raise ErroRequisicao(404, "Rota pessoal não encontrada.")
        id_usuario = self._id_sessao(token)

        if rota == "/api/pessoal/conta" and metodo == "GET":
            codigo, resultado = self._servico.processar("GET", f"/api/usuarios/{id_usuario}")
            return codigo, resultado, None
        if rota == "/api/pessoal/conta" and metodo == "PATCH":
            if not isinstance(dados, dict) or set(dados) != {"nome"}:
                raise ErroRequisicao(400, "Na área pessoal só é permitido alterar o nome.")
            codigo, resultado = self._servico.processar("PATCH", f"/api/usuarios/{id_usuario}", dados)
            return codigo, resultado, None
        if rota == "/api/pessoal/resgates" and metodo == "POST":
            if not isinstance(dados, dict) or set(dados) != {"tipo"}:
                raise ErroRequisicao(400, "Informe apenas o tipo de passagem.")
            codigo, resultado = self._servico.processar("POST", f"/api/usuarios/{id_usuario}/resgates", dados)
            return codigo, resultado, None
        raise ErroRequisicao(405, "Operação não permitida na área pessoal.")
