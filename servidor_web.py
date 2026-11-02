"""Servidor HTTP local do Zyra para demonstrar integração web com o Oracle.

Execute `python servidor_web.py` e abra http://127.0.0.1:8765/.
Restrito à própria máquina: não há autenticação de usuários neste protótipo.
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from servico_web import ErroRequisicao, ServicoZyra


PASTA_PAINEL = Path(__file__).resolve().parent / "painel_web"
TAMANHO_MAX_JSON = 16 * 1024


def criar_servidor(porta=8765, servico=None):
    """Inicializa servidor somente em loopback; aceita serviço injetável para testes."""
    app = servico if servico is not None else ServicoZyra()
    origens = {
        f"http://127.0.0.1:{porta}", f"http://localhost:{porta}",
        "http://127.0.0.1:5173", "http://localhost:5173",  # React/Vite local
    }

    class Roteador(BaseHTTPRequestHandler):
        """Adapta HTTP/JSON ao serviço de regras da aplicação."""

        def _cabecalhos(self, codigo, formato="application/json; charset=utf-8", tamanho=0):
            self.send_response(codigo)
            self.send_header("Content-Type", formato)
            self.send_header("Content-Length", str(tamanho))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Vary", "Origin")
            origem = self.headers.get("Origin")
            if origem in origens:
                self.send_header("Access-Control-Allow-Origin", origem)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Zyra-Cliente")
            self.end_headers()

        def _json(self, codigo, objeto):
            texto = json.dumps(objeto, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self._cabecalhos(codigo, tamanho=len(texto))
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

        def _executar(self):
            if not self._origem_permitida():
                return
            rota = urlsplit(self.path).path
            if self.command == "GET" and rota in ("/", "/painel.js", "/painel.css"):
                arquivos = {
                    "/": ("index.html", "text/html; charset=utf-8"),
                    "/painel.js": ("painel.js", "text/javascript; charset=utf-8"),
                    "/painel.css": ("painel.css", "text/css; charset=utf-8"),
                }
                nome, formato = arquivos[rota]
                conteudo = (PASTA_PAINEL / nome).read_bytes()
                self._cabecalhos(200, formato, len(conteudo))
                self.wfile.write(conteudo)
                return
            if rota in ("/", "/painel.js", "/painel.css"):
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


def main():
    """Verifica conexão Oracle e inicia painel web no computador local."""
    parser = argparse.ArgumentParser(description="Painel web local Zyra")
    parser.add_argument("--porta", type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.porta <= 65535:
        parser.error("Use uma porta entre 1024 e 65535.")
    try:
        from banco import conectar
        conexao = conectar()
        conexao.close()
    except Exception as erro:
        print(f"Não foi possível conectar ao Oracle: {erro}")
        print("Verifique o .env e execute python testar_banco.py.")
        return

    servidor = criar_servidor(args.porta)
    print(f"Zyra Web disponível em http://127.0.0.1:{args.porta}/")
    print("Somente acesso local. Pressione Ctrl+C para encerrar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nPainel encerrado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
