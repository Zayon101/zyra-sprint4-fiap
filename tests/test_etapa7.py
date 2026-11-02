"""Testes da ponte web e do servidor HTTP; sem Oracle e sem internet."""

from contextlib import contextmanager
from http.client import HTTPConnection
import json
from threading import Thread
import unittest

from zyra.integrations.api_clima import CatalogoClima, ErroAPI
from zyra.database.repositorio import RepositorioOracle
from zyra.web.servidor import criar_servidor
from zyra.web.servico import ErroRequisicao, ServicoZyra
from tests.oracle_simulado import ConexaoSimulada
from tests.test_etapa6 import DADOS
from zyra.integrations.api_clima import processar_resposta


class TesteServicoWeb(unittest.TestCase):
    def setUp(self):
        self.conexao = ConexaoSimulada()
        self.repo = RepositorioOracle(self.conexao)

        @contextmanager
        def factory():
            yield self.repo

        self.servico = ServicoZyra(
            repositorio_factory=factory,
            catalogo_clima=CatalogoClima(consultar=lambda: processar_resposta(DADOS)),
        )

    def tearDown(self):
        self.conexao.close()

    def requisitar(self, metodo, rota, dados=None):
        return self.servico.processar(metodo, rota, dados)

    def assertErro(self, codigo, metodo, rota, dados=None):
        with self.assertRaises(ErroRequisicao) as contexto:
            self.requisitar(metodo, rota, dados)
        self.assertEqual(contexto.exception.status, codigo)

    def test_status_catalogo_e_clima_sem_oracle(self):
        self.assertEqual(self.requisitar("GET", "/api/status")[1]["status"], "ok")
        _, passagens = self.requisitar("GET", "/api/passagens")
        self.assertEqual([p["custo_pontos"] for p in passagens["passagens"]], [587, 1174, 2935])
        self.assertEqual(self.requisitar("GET", "/api/clima")[1]["cidade"], "São Paulo")

    def test_crud_e_resgate_reais_no_repositorio_simulado(self):
        codigo, dados = self.requisitar("POST", "/api/usuarios", {"nome": "Ana Maria"})
        self.assertEqual(codigo, 201)
        id_usuario = dados["usuario"]["id"]
        self.assertEqual(dados["usuario"]["pontos"], 500)
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["nome"], "Ana Maria")

        codigo, dados = self.requisitar("GET", "/api/usuarios")
        self.assertEqual(len(dados["usuarios"]), 1)
        self.assertEqual(codigo, 200)
        self.requisitar("PATCH", f"/api/usuarios/{id_usuario}", {"nome": "Ana Paula"})
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["nome"], "Ana Paula")
        self.requisitar("PATCH", f"/api/usuarios/{id_usuario}", {"pontos": 500})
        _, dados = self.requisitar("POST", f"/api/usuarios/{id_usuario}/pontos", {"quantidade": 100})
        self.assertEqual(dados["usuario"]["pontos"], 600)
        codigo, dados = self.requisitar("POST", f"/api/usuarios/{id_usuario}/resgates", {"tipo": 1})
        self.assertEqual(codigo, 201)
        self.assertEqual(dados["usuario"]["pontos"], 13)
        self.assertEqual(len(dados["usuario"]["historico"]), 1)
        self.assertErro(409, "POST", f"/api/usuarios/{id_usuario}/resgates", {"tipo": 1})
        self.assertEqual(len(self.repo.consultar_usuario(id_usuario)["historico"]), 1)
        self.assertEqual(self.requisitar("GET", "/api/resumo")[1]["total_viagens"], 1)
        self.assertEqual(self.requisitar("DELETE", f"/api/usuarios/{id_usuario}")[0], 200)
        self.assertErro(404, "GET", f"/api/usuarios/{id_usuario}")

    def test_erros_de_validacao_nao_modificam_banco(self):
        self.assertErro(400, "POST", "/api/usuarios", {"nome": "A"})
        self.assertErro(400, "POST", "/api/usuarios", {"nome": "Ana", "pontos": 999})
        self.assertErro(400, "POST", "/api/usuarios", {"nome": None})
        id_usuario = self.repo.criar_usuario("Ana Maria")
        self.assertErro(400, "PATCH", f"/api/usuarios/{id_usuario}", {"nome": "B", "pontos": 0})
        self.assertErro(400, "PATCH", f"/api/usuarios/{id_usuario}", {"pontos": True})
        self.assertErro(400, "POST", f"/api/usuarios/{id_usuario}/pontos", {"quantidade": 0})
        self.assertErro(400, "POST", f"/api/usuarios/{id_usuario}/resgates", {"tipo": True})
        self.assertErro(400, "POST", f"/api/usuarios/{id_usuario}/resgates", {"tipo": 4})
        self.assertErro(404, "GET", "/api/usuarios/0")
        self.assertErro(404, "GET", "/api/usuarios/aaa")
        self.assertErro(404, "GET", "/api/usuarios/999")
        self.assertErro(404, "DELETE", "/api/usuarios/999")
        self.assertErro(404, "POST", "/api/usuarios/999/pontos", {"quantidade": 10})
        self.assertErro(404, "POST", "/api/usuarios/999/resgates", {"tipo": 1})
        self.assertErro(404, "GET", "/api/inexistente")
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["pontos"], 500)

    def test_clima_indisponivel_retorna_erro_sem_modificar_oracle(self):
        self.servico._clima = CatalogoClima(consultar=lambda: (_ for _ in ()).throw(ErroAPI("Clima indisponível")))
        self.assertErro(502, "GET", "/api/clima")
        self.assertEqual(self.repo.listar_usuarios(), [])


class TesteHttpLocal(unittest.TestCase):
    def setUp(self):
        # Serviço mockado: teste de transporte HTTP, não de regras SQL.
        class AppTeste:
            def processar(self, metodo, rota, dados=None):
                if not rota.startswith("/api/"):
                    raise ErroRequisicao(404, "Rota não encontrada.")
                return 200, {"metodo": metodo, "rota": rota, "dados": dados, "acao": "ok"}
        self.servidor = criar_servidor(0, AppTeste())
        self.porta = self.servidor.server_address[1]
        self.thread = Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.thread.join(timeout=2)

    def http(self, metodo, rota, payload=None, headers=None):
        conexao = HTTPConnection("127.0.0.1", self.porta, timeout=4)
        try:
            cabecalhos = headers or {}
            corpo = None if payload is None else json.dumps(payload).encode("utf-8")
            conexao.request(metodo, rota, body=corpo, headers=cabecalhos)
            resposta = conexao.getresponse()
            return resposta.status, dict(resposta.getheaders()), resposta.read()
        finally:
            conexao.close()

    def test_painel_e_arquivos_estaticos(self):
        for rota, tipo in (("/", "text/html"), ("/painel.js", "text/javascript"), ("/painel.css", "text/css")):
            with self.subTest(rota=rota):
                status, headers, conteudo = self.http("GET", rota)
                self.assertEqual(status, 200)
                self.assertIn(tipo, headers["Content-Type"])
                self.assertGreater(len(conteudo), 200)
        status, _, _ = self.http("GET", "/painel/../.env")
        self.assertEqual(status, 404)  # Impede exposição de arquivos como .env.

    def test_post_json_e_cors_do_vite(self):
        status, headers, corpo = self.http("POST", "/api/usuarios", {"nome": "Ana Maria"}, {
            "Origin": "http://localhost:5173", "Content-Type": "application/json", "X-Zyra-Cliente": "painel-web",
        })
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "http://localhost:5173")
        self.assertEqual(json.loads(corpo)["dados"]["nome"], "Ana Maria")

    def test_bloqueia_origem_nao_autorizada(self):
        status, headers, corpo = self.http("POST", "/api/usuarios", {"nome": "Ana"}, {
            "Origin": "https://site-externo.example", "Content-Type": "application/json", "X-Zyra-Cliente": "painel-web",
        })
        self.assertEqual(status, 403)
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertIn("Origem não autorizada", corpo.decode())

    def test_impede_post_sem_cabecalho_especial(self):
        status, _, _ = self.http("POST", "/api/usuarios", {"nome": "Ana"}, {"Content-Type": "application/json"})
        self.assertEqual(status, 403)

    def test_rejeita_json_invalido_e_content_type_indevido(self):
        status, _, _ = self.http("POST", "/api/usuarios", {"nome": "Ana"}, {"X-Zyra-Cliente": "painel-web", "Content-Type": "text/plain"})
        self.assertEqual(status, 415)
        status, _, _ = self.http("POST", "/api/usuarios", None, {"X-Zyra-Cliente": "painel-web", "Content-Type": "application/json"})
        self.assertEqual(status, 413)

    def test_options_preflight(self):
        status, headers, corpo = self.http("OPTIONS", "/api/usuarios", headers={"Origin": "http://localhost:5173"})
        self.assertEqual(status, 204)
        self.assertEqual(corpo, b"")
        self.assertIn("PATCH", headers["Access-Control-Allow-Methods"])


class TesteIntegracaoHttpSimulada(unittest.TestCase):
    """Garante ciclo web → API → repositório SQL via conexão SQLite simulada."""

    http = TesteHttpLocal.http

    def setUp(self):
        self.conexao = ConexaoSimulada(permitir_multiplas_threads=True)
        repo = RepositorioOracle(self.conexao)

        @contextmanager
        def factory():
            yield repo

        app = ServicoZyra(repositorio_factory=factory,
                          catalogo_clima=CatalogoClima(consultar=lambda: processar_resposta(DADOS)))
        self.servidor = criar_servidor(0, app)
        self.porta = self.servidor.server_address[1]
        self.thread = Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        TesteHttpLocal.tearDown(self)
        self.conexao.close()

    def test_cadastrar_editar_resgatar_e_consultar_por_http_real(self):
        headers = {"X-Zyra-Cliente": "painel-web", "Content-Type": "application/json"}
        codigo, _, corpo = self.http("POST", "/api/usuarios", {"nome": "Ana Maria"}, headers)
        self.assertEqual(codigo, 201)
        usuario = json.loads(corpo)["usuario"]
        self.assertEqual(usuario["pontos"], 500)
        id_usuario = usuario["id"]

        codigo, _, corpo = self.http("POST", f"/api/usuarios/{id_usuario}/pontos", {"quantidade": 100}, headers)
        self.assertEqual(codigo, 200)
        self.assertEqual(json.loads(corpo)["usuario"]["pontos"], 600)

        codigo, _, corpo = self.http("POST", f"/api/usuarios/{id_usuario}/resgates", {"tipo": 1}, headers)
        self.assertEqual(codigo, 201)
        self.assertEqual(json.loads(corpo)["usuario"]["pontos"], 13)

        codigo, _, corpo = self.http("GET", f"/api/usuarios/{id_usuario}")
        self.assertEqual(codigo, 200)
        self.assertEqual(json.loads(corpo)["usuario"]["historico"][0]["custo"], 587)

        codigo, _, corpo = self.http("DELETE", f"/api/usuarios/{id_usuario}", headers=headers)
        self.assertEqual(codigo, 200)
        self.assertIsNone(RepositorioOracle(self.conexao).consultar_usuario(id_usuario))


if __name__ == "__main__":
    unittest.main()
