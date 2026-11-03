"""Servidor HTTP local do Zyra com API e página React compilada.

Iniciado pelo menu do arquivo main.py; disponível em 127.0.0.1:8765.
A aplicação deve permanecer no computador local.
"""

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie, CookieError
from pathlib import Path
from urllib.parse import urlsplit, unquote

from api.servico import ErroRequisicao, ServicoZyra
from api.pessoal import COOKIE_NOME, ServicoPessoal


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTAS_FRONTEND = (
    RAIZ_PROJETO / "frontend" / "zyra-app" / "dist",
    RAIZ_PROJETO / "frontend" / "dist",
)
TAMANHO_MAX_JSON = 16 * 1024


def localizar_frontend() -> Path | None:
    """Localiza o build React, inclusive quando o aplicativo está em frontend/zyra-app.

    A verificação é feita a cada acesso, permitindo compilar o React
    sem precisar reiniciar o servidor Python.
    """
    return next((pasta for pasta in PASTAS_FRONTEND if (pasta / "index.html").is_file()), None)


def criar_servidor(porta=8765, servico=None, banco_disponivel=True):
    """Inicializa servidor somente em loopback; aceita serviço injetável para testes."""
    app = servico if servico is not None else ServicoZyra(banco_disponivel=banco_disponivel)
    pessoal = ServicoPessoal(app)
    origens = {
        f"http://127.0.0.1:{porta}", f"http://localhost:{porta}",
        "http://127.0.0.1:5173", "http://localhost:5173",  # React/Vite local
    }

    class Roteador(BaseHTTPRequestHandler):
        """Adapta HTTP/JSON ao serviço de regras da aplicação."""

        def _cabecalhos(self, codigo, formato="application/json; charset=utf-8", tamanho=0, cookie=None):
            self.send_response(codigo)
            self.send_header("Content-Type", formato)
            self.send_header("Content-Length", str(tamanho))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Vary", "Origin")
            if cookie is not None:
                self.send_header("Set-Cookie", cookie)
            origem = self.headers.get("Origin")
            if origem in origens:
                self.send_header("Access-Control-Allow-Origin", origem)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Zyra-Cliente")
            self.end_headers()

        def _json(self, codigo, objeto, cookie=None):
            texto = json.dumps(objeto, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self._cabecalhos(codigo, tamanho=len(texto), cookie=cookie)
            self.wfile.write(texto)

        def _erro(self, codigo, mensagem):
            self._json(codigo, {"erro": mensagem})

        def _origem_permitida(self):
            origem = self.headers.get("Origin")
            if origem is not None and origem not in origens:
                self._erro(403, "Origem não autorizada.")
                return False
            return True

        def _corpo_json(self):
            if self.headers.get_content_type() != "application/json":
                raise ErroRequisicao(415, "Envie Content-Type: application/json.")
            texto_tamanho = self.headers.get("Content-Length", "")
            if not texto_tamanho.isascii() or not texto_tamanho.isdecimal():
                raise ErroRequisicao(411, "Envie Content-Length válido.")
            tamanho = int(texto_tamanho)
            if tamanho < 1 or tamanho > TAMANHO_MAX_JSON:
                raise ErroRequisicao(413, "JSON vazio ou muito grande.")
            try:
                texto = self.rfile.read(tamanho).decode("utf-8")
                return json.loads(texto)
            except (UnicodeDecodeError, json.JSONDecodeError) as erro:
                raise ErroRequisicao(400, "JSON inválido.") from erro

        def _arquivo_frontend(self, rota: str) -> None:
            """Entrega assets do build do React e aplica fallback às rotas SPA."""
            pasta_frontend = localizar_frontend()
            if pasta_frontend is None:
                pagina = (
                    "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
                    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                    "<title>Zyra — Página web</title>"
                    "<style>body{font:16px system-ui,sans-serif;background:#f7f8fa;"
                    "color:#232b35;margin:0;min-height:100vh;display:grid;place-items:center}"
                    "main{background:white;max-width:560px;margin:20px;padding:35px;"
                    "border:1px solid #e0e4e9;border-radius:16px}"
                    "a{color:#1e6b5d}code{background:#f1f3f5;padding:3px 5px}</style>"
                    "</head><body><main><h1>Zyra 🚇</h1>"
                    "<h2>Servidor web funcionando!</h2>"
                    + ("<p style='color:#914d00'><strong>Oracle ainda não preparado.</strong> "
                       "O painel pode abrir, mas cadastros, saldos e históricos "
                       "precisam da conexão no menu [7].</p>" if not banco_disponivel else "")
                    + "<p>O servidor Python está funcionando, mas não encontrou o "
                    "React compilado. Execute <code>npm run build</code> "
                    "na pasta <code>frontend/zyra-app</code> e atualize esta página.</p>"
                    "<p><a href='/api/status'>Testar status da API</a> · "
                    "<a href='/api/passagens'>Consultar passagens</a></p>"
                    "<p>O build deve ficar em <code>frontend/zyra-app/dist/</code> "
                    "(ou <code>frontend/dist/</code>).</p></main></body></html>"
                )
                conteudo = pagina.encode("utf-8")
                self._cabecalhos(200, "text/html; charset=utf-8", len(conteudo))
                self.wfile.write(conteudo)
                return

            # Arquivos de build são públicos, mas caminhos fora de dist não são.
            relativo = unquote(rota).lstrip("/")
            if any(item.startswith(".") for item in Path(relativo).parts):
                self._erro(404, "Arquivo não encontrado.")
                return
            raiz = pasta_frontend.resolve()
            destino = (raiz / relativo).resolve()
            if not destino.is_relative_to(raiz):
                self._erro(404, "Arquivo não encontrado.")
                return
            if not destino.is_file():
                # React Router usa rotas sem extensão; não mascarar assets ausentes.
                if Path(relativo).suffix or relativo.startswith("assets/"):
                    self._erro(404, "Arquivo não encontrado.")
                    return
                destino = raiz / "index.html"
            conteudo = destino.read_bytes()
            formato = mimetypes.guess_type(str(destino))[0] or "application/octet-stream"
            if formato.startswith("text/") or formato == "application/javascript":
                formato += "; charset=utf-8"
            self._cabecalhos(200, formato, len(conteudo))
            self.wfile.write(conteudo)

        def _executar(self):
            if not self._origem_permitida():
                return
            rota = urlsplit(self.path).path
            if not rota.startswith("/api/") and rota != "/api":
                if self.command == "GET":
                    self._arquivo_frontend(rota)
                else:
                    self._erro(405, "Método não permitido.")
                return
            if self.command in ("POST", "PATCH", "DELETE"):
                # Origem autorizada + cabeçalho não simples bloqueiam POSTs de páginas externas.
                if self.headers.get("X-Zyra-Cliente") != "painel-web":
                    self._erro(403, "Cabeçalho X-Zyra-Cliente ausente.")
                    return
                dados = self._corpo_json() if self.command in ("POST", "PATCH") else None
            else:
                dados = None
            if rota.startswith("/api/pessoal/"):
                cookie_bruto = self.headers.get("Cookie", "")
                token = None
                try:
                    cookies = SimpleCookie()
                    cookies.load(cookie_bruto[:2048])
                    if COOKIE_NOME in cookies:
                        token = cookies[COOKIE_NOME].value
                except CookieError:
                    pass
                codigo, resposta, cookie_resposta = pessoal.processar(self.command, rota, dados, token)
                self._json(codigo, resposta, cookie_resposta)
                return
            codigo, resposta = app.processar(self.command, rota, dados)
            self._json(codigo, resposta)

        def do_OPTIONS(self):
            if not self._origem_permitida():
                return
            self._cabecalhos(204)

        def do_GET(self):
            self._tratar()

        def do_POST(self):
            self._tratar()

        def do_PATCH(self):
            self._tratar()

        def do_DELETE(self):
            self._tratar()

        def _tratar(self):
            try:
                self._executar()
            except ErroRequisicao as erro:
                self._erro(erro.status, str(erro))
            except OSError:
                self._erro(503, "Recurso local indisponível.")
            except Exception:
                # Não enviar stacktrace, SQL ou credenciais ao navegador.
                self._erro(500, "Falha interna no serviço Zyra.")

    return ThreadingHTTPServer(("127.0.0.1", porta), Roteador)

