"""Testes do CRUD Oracle com simulação de SQL e transações usando SQLite."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.importar_json import importar_no_oracle, validar_arquivo_json
from zyra.database.repositorio import ErroBanco, RepositorioOracle
from tests.oracle_simulado import ConexaoSimulada


class TestesEtapa3(unittest.TestCase):
    def setUp(self):
        self.conexao = ConexaoSimulada()
        self.repo = RepositorioOracle(self.conexao)

    def tearDown(self):
        if not self.conexao.fechada:
            self.conexao.close()

    def test_crud_oracle_completo_e_persistencia_dentro_da_conexao(self):
        id_usuario = self.repo.criar_usuario("Ana Maria")
        self.assertGreater(id_usuario, 0)
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["pontos"], 500)
        self.assertEqual(len(self.repo.listar_usuarios()), 1)
        self.assertTrue(self.repo.alterar_nome(id_usuario, "Ana Paula"))
        self.assertTrue(self.repo.alterar_pontos(id_usuario, 700))
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["nome"], "Ana Paula")
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["pontos"], 700)
        self.assertTrue(self.repo.excluir_usuario(id_usuario))
        self.assertEqual(self.repo.listar_usuarios(), [])
        self.assertEqual(self.conexao.commits, 4)

    def test_usuarios_inexistentes_nao_sao_alterados(self):
        self.assertIsNone(self.repo.consultar_usuario(999))
        self.assertFalse(self.repo.alterar_nome(999, "Ana Maria"))
        self.assertFalse(self.repo.alterar_pontos(999, 100))
        self.assertFalse(self.repo.excluir_usuario(999))

    def test_ids_automaticos_nao_reutilizados(self):
        id1 = self.repo.criar_usuario("Ana Maria")
        self.repo.excluir_usuario(id1)
        id2 = self.repo.criar_usuario("Bia Souza")
        self.assertGreater(id2, id1)

    def test_sql_parametrizado_aceita_nome_com_apostrofo_sem_injecao(self):
        id_usuario = self.repo.criar_usuario("Ana O'Connor")
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["nome"], "Ana O'Connor")
        self.assertTrue(self.repo.alterar_nome(id_usuario, "Joana D'Arc"))
        self.assertEqual(len(self.repo.listar_usuarios()), 1)

    def test_pontos_e_troca_persistidos_no_banco(self):
        id_usuario = self.repo.criar_usuario("Ana Maria")
        self.assertEqual(self.repo.adicionar_pontos(id_usuario, 100), 600)
        self.assertEqual(self.repo.resgatar_passagem(id_usuario, 0), (True, 13))
        usuario = self.repo.consultar_usuario(id_usuario)
        self.assertEqual(usuario["pontos"], 13)
        self.assertEqual(len(usuario["historico"]), 1)
        self.assertEqual(usuario["historico"][0]["custo"], 587)
        self.assertEqual(usuario["historico"][0]["valor"], 5.4)
        self.assertEqual(self.repo.resgatar_passagem(id_usuario, 0), (False, 13))
        self.assertEqual(len(self.repo.consultar_usuario(id_usuario)["historico"]), 1)

    def test_rollback_ao_falhar_insert_da_troca(self):
        id_usuario = self.repo.criar_usuario("Ana Maria")
        self.repo.adicionar_pontos(id_usuario, 100)
        self.conexao.falha_na_troca = True
        with self.assertRaisesRegex(ErroBanco, "resgate"):
            self.repo.resgatar_passagem(id_usuario, 0)
        self.conexao.falha_na_troca = False
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["pontos"], 600)
        self.assertEqual(self.repo.consultar_usuario(id_usuario)["historico"], [])
        self.assertGreater(self.conexao.rollbacks, 0)

    def test_validacao_de_saldo_e_quantidade(self):
        id_usuario = self.repo.criar_usuario("Ana Maria")
        for invalido in (-1, 1.5, True):
            with self.subTest(invalido=invalido), self.assertRaises(ValueError):
                self.repo.alterar_pontos(id_usuario, invalido)
        for invalido in (-1, 0, True, 3.2):
            with self.subTest(invalido=invalido), self.assertRaises(ValueError):
                self.repo.adicionar_pontos(id_usuario, invalido)
        with self.assertRaises(ValueError):
            self.repo.resgatar_passagem(id_usuario, 99)

    def test_importacao_opcional_preserva_historico_com_novos_ids(self):
        usuario = {"id": 8, "nome": "Ana Maria", "pontos": 13,
                   "historico": [{"passagem": "Unitária", "viagens": 1,
                                  "custo": 587, "valor": 5.4}]}
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados_zyra.json"
            caminho.write_text(json.dumps([usuario]), encoding="utf-8")
            dados = validar_arquivo_json(caminho)
        ids = importar_no_oracle(self.repo, dados)
        self.assertEqual(ids, {8: 1})
        resultado = self.repo.consultar_usuario(1)
        self.assertEqual(resultado["historico"][0]["valor"], 5.4)
        self.assertEqual(resultado["pontos"], 13)
        with self.assertRaisesRegex(ValueError, "duplicados"):
            importar_no_oracle(self.repo, dados)

    def test_importacao_rejeita_json_invalido_sem_inserir(self):
        for objeto in ([{"id": 1, "nome": "Ana", "pontos": -100, "historico": []}],
                       [{"id": 1, "nome": "Ana", "pontos": 500, "historico": [{}]}],
                       {"id": 1}):
            with self.subTest(objeto=objeto), tempfile.TemporaryDirectory() as pasta:
                caminho = Path(pasta) / "dados_zyra.json"
                caminho.write_text(json.dumps(objeto), encoding="utf-8")
                with self.assertRaises(ValueError):
                    validar_arquivo_json(caminho)
        self.assertEqual(self.repo.listar_usuarios(), [])

    def test_menu_crud_interativo(self):
        from zyra.cli.menus import menu_crud
        entradas = ["1", "Ana Maria", "", "2", "", "3", "1", "",
                    "4", "1", "1", "Ana Clara", "", "5", "1", "1", "", "0"]
        with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(io.StringIO()) as saida:
            menu_crud(self.repo)
        self.assertEqual(self.repo.listar_usuarios(), [])
        self.assertIn("Usuário cadastrado com sucesso", saida.getvalue())
        self.assertIn("Usuário excluído com sucesso", saida.getvalue())

    def test_interface_completa_com_pontos_resgate_e_historico(self):
        from zyra.cli import app as main
        entradas = [
            "",       # boas-vindas
            "1", "1", "Ana Maria", "", "0",  # cadastrar
            "2", "1", "100", "",              # adicionar 100 pontos
            "3", "1", "", "0",                 # resgatar uma passagem
            "3", "",                          # consultar histórico
            "4", "",                          # resumo
            "0",                              # sair
        ]
        with (patch("zyra.cli.app.conectar", return_value=self.conexao),
              patch("builtins.input", side_effect=entradas),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            main.main()
        self.assertTrue(self.conexao.fechada)
        texto = saida.getvalue()
        self.assertIn("Troca realizada com sucesso", texto)
        self.assertIn("Total de viagens resgatadas: 1", texto)
        self.assertIn("13 pontos", texto)
        self.assertIn("Histórico de Ana Maria", texto)
        # Já fechada pelo main; tearDown será ajustado abaixo.

    def test_falha_de_conexao_nao_abre_menus(self):
        from zyra.cli import app as main
        with (patch("zyra.cli.app.conectar", side_effect=ValueError("Teste de falha")),
              patch("zyra.cli.app.exibir_menu") as menu,
              contextlib.redirect_stdout(io.StringIO()) as saida):
            main.main()
        menu.assert_not_called()
        self.assertIn("Não foi possível conectar", saida.getvalue())

    def test_exclusao_cancelada_pelo_usuario(self):
        from zyra.cli.usuarios import excluir_usuario
        id_usuario = self.repo.criar_usuario("Ana Maria")
        with patch("builtins.input", side_effect=[str(id_usuario), "2", ""]), contextlib.redirect_stdout(io.StringIO()):
            excluir_usuario(self.repo)
        self.assertIsNotNone(self.repo.consultar_usuario(id_usuario))


if __name__ == "__main__":
    unittest.main()
