"""Validação de sessões demonstrativas e escopo da área pessoal."""
from contextlib import contextmanager
from http.client import HTTPConnection
import json
from threading import Thread
import unittest

from tests.oracle_simulado import ConexaoSimulada
from zyra.database.repositorio import RepositorioOracle
from zyra.web.pessoal import ServicoPessoal
from zyra.web.servidor import criar_servidor
from zyra.web.servico import ErroRequisicao, ServicoZyra


class TestesServicoPessoal(unittest.TestCase):
    def setUp(self):
        self.conexao = ConexaoSimulada()
        self.repo = RepositorioOracle(self.conexao)

        @contextmanager
        def factory():
            yield self.repo

        self.servico = ServicoPessoal(ServicoZyra(repositorio_factory=factory))
        self.id_ana = self.repo.criar_usuario('Ana Maria')
        self.id_bia = self.repo.criar_usuario('Bia Santos')

    def tearDown(self):
        self.conexao.close()

    def entrar(self, identificador):
        codigo, dados, cookie = self.servico.processar('POST', '/api/pessoal/entrar', {'identificador': identificador})
        self.assertEqual(codigo, 200)
        token = cookie.split(';')[0].split('=', 1)[1]
        return dados, token

    def test_identificacao_por_id_ou_nome_sem_listar_outras_contas(self):
        conta, token = self.entrar(str(self.id_ana))
        self.assertEqual(conta['usuario']['id'], self.id_ana)
        _, resposta, _ = self.servico.processar('GET', '/api/pessoal/conta', token=token)
        self.assertEqual(resposta['usuario']['nome'], 'Ana Maria')
        conta_bia, outro_token = self.entrar('bia santos')
        self.assertEqual(conta_bia['usuario']['id'], self.id_bia)
        self.assertNotEqual(token, outro_token)

    def test_sessao_limita_escrita_a_nome_e_resgates_da_conta(self):
        _, token = self.entrar('Ana Maria')
        for dados in ({'pontos': 10000}, {'nome': 'Ana Nova', 'pontos': 1}, {'id': self.id_bia, 'nome': 'Ana Nova'}):
            with self.subTest(dados=dados), self.assertRaises(ErroRequisicao) as erro:
                self.servico.processar('PATCH', '/api/pessoal/conta', dados, token)
            self.assertEqual(erro.exception.status, 400)
        codigo, _, _ = self.servico.processar('PATCH', '/api/pessoal/conta', {'nome': 'Ana Nova'}, token)
        self.assertEqual(codigo, 200)
        self.assertEqual(self.repo.consultar_usuario(self.id_ana)['nome'], 'Ana Nova')
        self.assertEqual(self.repo.consultar_usuario(self.id_bia)['nome'], 'Bia Santos')
        with self.assertRaises(ErroRequisicao) as erro:
            self.servico.processar('POST', '/api/pessoal/resgates', {'tipo': 1, 'id': self.id_bia}, token)
        self.assertEqual(erro.exception.status, 400)
        self.repo.adicionar_pontos(self.id_ana, 100)
        codigo, resultado, _ = self.servico.processar('POST', '/api/pessoal/resgates', {'tipo': 1}, token)
        self.assertEqual(codigo, 201)
        self.assertEqual(resultado['usuario']['pontos'], 13)
        self.assertEqual(self.repo.consultar_usuario(self.id_bia)['pontos'], 500)

    def test_rejeita_sessao_ausente_e_id_invalido(self):
        for valor in ({'identificador': ''}, {'identificador': -2}, {'id': self.id_ana}, {'identificador': '0'}):
            with self.subTest(valor=valor), self.assertRaises(ErroRequisicao):
                self.servico.processar('POST', '/api/pessoal/entrar', valor)
        with self.assertRaises(ErroRequisicao) as erro:
            self.servico.processar('GET', '/api/pessoal/conta')
        self.assertEqual(erro.exception.status, 401)
        with self.assertRaises(ErroRequisicao) as erro:
            self.servico.processar('GET', '/api/pessoal/conta', token='forjado')
        self.assertEqual(erro.exception.status, 401)

    def test_nome_longo_compativel_com_limite_do_oracle(self):
        """Um cadastro de 120 caracteres também deve poder entrar por nome."""
        nome = 'Ana ' + 'Maria' * 23 + 'X'  # 120 caracteres
        self.assertEqual(len(nome), 120)
        identificador = self.repo.criar_usuario(nome)
        conta, _ = self.entrar(nome)
        self.assertEqual(conta['usuario']['id'], identificador)
        with self.assertRaises(ErroRequisicao) as erro:
            self.servico.processar('POST', '/api/pessoal/entrar', {'identificador': nome + 'Y'})
        self.assertEqual(erro.exception.status, 400)

    def test_nomes_repetidos_exigem_id(self):
        self.repo.criar_usuario('Ana Maria')
        with self.assertRaises(ErroRequisicao) as erro:
            self.entrar('ANA MARIA')
        self.assertEqual(erro.exception.status, 409)
        self.entrar(str(self.id_ana))

    def test_sair_invalida_sessao(self):
        _, token = self.entrar('Bia Santos')
        _, resposta, cookie = self.servico.processar('POST', '/api/pessoal/sair', {}, token)
        self.assertTrue(resposta['encerrada'])
        self.assertIn('Max-Age=0', cookie)
        with self.assertRaises(ErroRequisicao) as erro:
            self.servico.processar('GET', '/api/pessoal/conta', token=token)
        self.assertEqual(erro.exception.status, 401)

    def test_expiracao_sessao(self):
        _, token = self.entrar('Ana Maria')
        self.servico._sessoes[token] = (self.id_ana, 0)
        with self.assertRaises(ErroRequisicao) as erro:
            self.servico.processar('GET', '/api/pessoal/conta', token=token)
        self.assertEqual(erro.exception.status, 401)


class TestesHttpAreaPessoal(unittest.TestCase):
    def setUp(self):
        self.conexao = ConexaoSimulada(permitir_multiplas_threads=True)
        repo = RepositorioOracle(self.conexao)
        self.id_ana = repo.criar_usuario('Ana Maria')
        self.id_bia = repo.criar_usuario('Bia Santos')

        @contextmanager
        def factory():
            yield repo

        self.servidor = criar_servidor(0, ServicoZyra(repositorio_factory=factory))
        self.porta = self.servidor.server_address[1]
        self.thread = Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.thread.join(timeout=2)
        self.conexao.close()

    def http(self, metodo, rota, dados=None, cookie=None):
        conexao = HTTPConnection('127.0.0.1', self.porta, timeout=5)
        headers = {'Origin': 'http://localhost:5173'}
        if metodo != 'GET':
            headers['X-Zyra-Cliente'] = 'painel-web'
        if cookie:
            headers['Cookie'] = cookie
        if dados is not None:
            headers['Content-Type'] = 'application/json'
            corpo = json.dumps(dados)
        else:
            corpo = None
        try:
            conexao.request(metodo, rota, body=corpo, headers=headers)
            r = conexao.getresponse()
            return r.status, dict(r.getheaders()), json.loads(r.read())
        finally:
            conexao.close()

    def test_fluxo_http_sessao_pessoal_e_bloqueio_escopo(self):
        status, _, _ = self.http('GET', '/api/pessoal/conta')
        self.assertEqual(status, 401)
        status, headers, resposta = self.http('POST', '/api/pessoal/entrar', {'identificador': str(self.id_ana)})
        self.assertEqual(status, 200)
        self.assertEqual(resposta['usuario']['nome'], 'Ana Maria')
        self.assertIn('HttpOnly', headers['Set-Cookie'])
        self.assertIn('SameSite=Strict', headers['Set-Cookie'])
        cookie = headers['Set-Cookie'].split(';')[0]
        status, _, dados = self.http('GET', '/api/pessoal/conta', cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual(dados['usuario']['id'], self.id_ana)
        status, _, _ = self.http('PATCH', '/api/pessoal/conta', {'pontos': 10000}, cookie)
        self.assertEqual(status, 400)
        status, _, dados = self.http('PATCH', '/api/pessoal/conta', {'nome': 'Ana Paula'}, cookie)
        self.assertEqual(status, 200)
        self.assertEqual(dados['usuario']['nome'], 'Ana Paula')
        status, _, _ = self.http('POST', '/api/pessoal/resgates', {'tipo': 1}, cookie)
        self.assertEqual(status, 409)
        status, _, _ = self.http('POST', '/api/pessoal/sair', {}, cookie)
        self.assertEqual(status, 200)
        status, _, _ = self.http('GET', '/api/pessoal/conta', cookie=cookie)
        self.assertEqual(status, 401)

    def test_mudancas_entre_admin_e_pessoal_sao_refletidas_no_oracle(self):
        """Duas áreas, um cadastro: operações intercaladas enxergam o mesmo saldo."""
        status, headers, resposta = self.http('POST', '/api/pessoal/entrar', {'identificador': str(self.id_ana)})
        self.assertEqual(status, 200)
        cookie = headers['Set-Cookie'].split(';')[0]
        self.assertEqual(resposta['usuario']['pontos'], 500)

        status, _, dados = self.http('POST', f'/api/usuarios/{self.id_ana}/pontos', {'quantidade': 100})
        self.assertEqual(status, 200)
        self.assertEqual(dados['usuario']['pontos'], 600)

        status, _, dados = self.http('GET', '/api/pessoal/conta', cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual(dados['usuario']['pontos'], 600)

        status, _, dados = self.http('POST', '/api/pessoal/resgates', {'tipo': 1}, cookie=cookie)
        self.assertEqual(status, 201)
        self.assertEqual(dados['usuario']['pontos'], 13)
        self.assertEqual(len(dados['usuario']['historico']), 1)

        status, _, dados = self.http('GET', f'/api/usuarios/{self.id_ana}')
        self.assertEqual(status, 200)
        self.assertEqual(dados['usuario']['pontos'], 13)
        self.assertEqual(len(dados['usuario']['historico']), 1)

        status, _, dados = self.http('PATCH', f'/api/usuarios/{self.id_ana}', {'nome': 'Ana Nova'})
        self.assertEqual(status, 200)
        status, _, dados = self.http('GET', '/api/pessoal/conta', cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual(dados['usuario']['nome'], 'Ana Nova')

        status, _, _ = self.http('DELETE', f'/api/usuarios/{self.id_ana}')
        self.assertEqual(status, 200)
        status, _, dados = self.http('GET', '/api/pessoal/conta', cookie=cookie)
        self.assertEqual(status, 404)
        self.assertEqual(dados['erro'], 'Usuário não encontrado.')

    def test_sessao_cada_cadastro(self):
        _, h1, _ = self.http('POST', '/api/pessoal/entrar', {'identificador': str(self.id_ana)})
        _, h2, _ = self.http('POST', '/api/pessoal/entrar', {'identificador': str(self.id_bia)})
        _, _, a = self.http('GET', '/api/pessoal/conta', cookie=h1['Set-Cookie'].split(';')[0])
        _, _, b = self.http('GET', '/api/pessoal/conta', cookie=h2['Set-Cookie'].split(';')[0])
        self.assertEqual(a['usuario']['id'], self.id_ana)
        self.assertEqual(b['usuario']['id'], self.id_bia)
        self.assertNotEqual(a['usuario']['id'], b['usuario']['id'])


if __name__ == '__main__':
    unittest.main()
