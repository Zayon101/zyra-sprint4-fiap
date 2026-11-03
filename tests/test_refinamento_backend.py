"""Regressões específicas do refinamento do backend (Lote 8E.1)."""

from contextlib import contextmanager, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.importar_json import validar_arquivo_json
from tests.oracle_simulado import ConexaoSimulada
from zyra.cli.app import main
from zyra.cli.utils import validar_nome
from zyra.core.modelos import Resumo, Troca, Usuario
from zyra.core.regras import validar_nome_usuario
from zyra.database.repositorio import ErroBanco, RepositorioOracle
from zyra.web.pessoal import ServicoPessoal
from zyra.web.servico import ServicoZyra, ErroRequisicao


class TestesRegrasCompartilhadas(unittest.TestCase):
    def test_api_e_terminal_aceitam_mesma_grafia(self):
        for entrada in ("Ana O'Connor", "João-Pedro", "D'Ávila", "Ana Maria", "Ana d’Ávila"):
            with self.subTest(entrada=entrada):
                self.assertEqual(validar_nome_usuario(entrada), entrada)
                with patch("builtins.input", return_value=entrada):
                    self.assertEqual(validar_nome(), entrada)

    def test_api_e_terminal_rejeitam_caracteres_invalidos(self):
        invalidos = ("Ana123", "Ana@Maria", "Ana\nMaria", "Ana\tMaria", "  ", "Ana😀")
        for nome in invalidos:
            with self.subTest(nome=repr(nome)):
                with self.assertRaises(ValueError):
                    validar_nome_usuario(nome)
                with (patch("builtins.input", side_effect=[nome, "Ana Maria"]),
                      redirect_stdout(io.StringIO())):
                    self.assertEqual(validar_nome(), "Ana Maria")

    def test_importacao_json_usa_a_mesma_validacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            usuario = {"id": 1, "nome": "Ana123", "pontos": 500, "historico": []}
            caminho.write_text(json.dumps([usuario]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nome inválido"):
                validar_arquivo_json(caminho)
            usuario["nome"] = "Ana O'Connor"
            caminho.write_text(json.dumps([usuario]), encoding="utf-8")
            self.assertEqual(validar_arquivo_json(caminho), [usuario])

    def test_modelos_declaram_campos_esperados(self):
        self.assertEqual(set(Usuario.__required_keys__), {"id", "nome", "pontos", "historico"})
        self.assertEqual(set(Troca.__required_keys__), {"id", "data", "passagem", "viagens", "custo", "valor"})
        self.assertEqual(len(Resumo.__required_keys__), 6)


class TestesConsultasEnxutas(unittest.TestCase):
    def setUp(self):
        self.conexao = ConexaoSimulada()
        self.repo = RepositorioOracle(self.conexao)

    def tearDown(self):
        self.conexao.close()

    def test_listagem_resumida_nao_consulta_trocas(self):
        identificador = self.repo.criar_usuario("Ana Maria")
        self.repo.adicionar_pontos(identificador, 100)
        self.repo.resgatar_passagem(identificador, 0)
        chamadas = []
        cursor_original = self.conexao.cursor

        def cursor_auditado():
            cursor = cursor_original()
            executar = cursor.execute
            def executar_auditado(sql, parametros=None):
                chamadas.append(sql.upper())
                return executar(sql, parametros)
            cursor.execute = executar_auditado
            return cursor

        with patch.object(self.conexao, "cursor", side_effect=cursor_auditado):
            usuario = self.repo.listar_usuarios(incluir_historico=False)[0]
        self.assertEqual(usuario["historico"], [])
        self.assertEqual(len(chamadas), 1)
        self.assertNotIn("ZYRA_TROCAS", chamadas[0])
        self.assertEqual(len(self.repo.listar_usuarios()[0]["historico"]), 1)

    def test_existe_cadastro_sem_carregar_lista(self):
        self.assertFalse(self.repo.possui_usuarios())
        identificador = self.repo.criar_usuario("Ana Maria")
        self.assertTrue(self.repo.possui_usuarios())
        self.repo.excluir_usuario(identificador)
        self.assertFalse(self.repo.possui_usuarios())

    def test_identificacao_nao_carrega_todos_os_historicos(self):
        self.repo.criar_usuario("Ana Maria")
        self.repo.criar_usuario("Bia Souza")
        @contextmanager
        def factory():
            yield self.repo
        servico = ServicoZyra(repositorio_factory=factory)
        pessoal = ServicoPessoal(servico)
        consultas = []
        original = self.repo.listar_usuarios
        def espiao(*args, **kwargs):
            consultas.append(kwargs.get("incluir_historico", True))
            return original(*args, **kwargs)
        with patch.object(self.repo, "listar_usuarios", side_effect=espiao):
            status, resultado, _ = pessoal.processar(
                "POST", "/api/pessoal/entrar", {"identificador": "Ana Maria"}
            )
        self.assertEqual(status, 200)
        self.assertEqual(resultado["usuario"]["nome"], "Ana Maria")
        self.assertEqual(consultas, [False])

    def test_valores_invalidos_rejeitados_pelo_servidor(self):
        @contextmanager
        def factory():
            yield self.repo
        servico = ServicoZyra(repositorio_factory=factory)
        for nome in ("Ana123", "João@Silva"):
            with self.subTest(nome=nome), self.assertRaises(ErroRequisicao) as contexto:
                servico.processar("POST", "/api/usuarios", {"nome": nome})
            self.assertEqual(contexto.exception.status, 400)
        self.assertFalse(self.repo.possui_usuarios())


class TestesTratamentoDeErros(unittest.TestCase):
    def test_interrupcao_em_submenu_fecha_conexao_sem_traceback(self):
        conexao = ConexaoSimulada()
        with (patch("zyra.cli.app.conectar", return_value=conexao),
              patch("builtins.input", side_effect=["", "1", KeyboardInterrupt()]),
              redirect_stdout(io.StringIO()) as saida):
            main()
        self.assertTrue(conexao.fechada)
        self.assertIn("interrompida", saida.getvalue())

    def test_erro_sql_explicita_causa(self):
        conexao = ConexaoSimulada()
        repo = RepositorioOracle(conexao)
        repo.criar_usuario("Ana Maria")
        with patch.object(conexao, "cursor", side_effect=RuntimeError("falha no driver")):
            with self.assertRaises(ErroBanco) as contexto:
                repo.listar_usuarios()
        self.assertIsInstance(contexto.exception.__cause__, RuntimeError)
        conexao.close()

    def test_falha_de_programacao_nao_e_disfarcada_de_erro_oracle(self):
        conexao = ConexaoSimulada()
        repo = RepositorioOracle(conexao)
        with patch.object(conexao, "cursor", side_effect=TypeError("contrato inválido")):
            with self.assertLogs("zyra.database.repositorio", "ERROR"):
                with self.assertRaises(TypeError):
                    repo.listar_usuarios()
        conexao.close()


if __name__ == "__main__":
    unittest.main()
