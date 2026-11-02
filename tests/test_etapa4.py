"""Regressões das regras de pontos, resgates e histórico da Etapa 4."""

import contextlib
from datetime import datetime
import io
import unittest
from unittest.mock import patch

from zyra.core.constantes import MAX_CARACTERES_NOME, MAX_PONTOS, TIPOS_PASSAGEM
from zyra.cli.operacoes import historico_trocas, resumo_sistema
from zyra.core.regras import (validar_credito, validar_indice_passagem,
                    validar_nome_usuario, validar_saldo)
from zyra.database.repositorio import ErroBanco, RepositorioOracle
from tests.oracle_simulado import ConexaoSimulada
from zyra.cli.utils import formatar_data_troca, validar_nome


class TestesEtapa4(unittest.TestCase):
    def setUp(self):
        self.conexao = ConexaoSimulada()
        self.repo = RepositorioOracle(self.conexao)

    def tearDown(self):
        if not self.conexao.fechada:
            self.conexao.close()

    def test_tipos_de_passagem_e_saldo_correspondente(self):
        usuario_id = self.repo.criar_usuario("Ana Maria")
        self.repo.adicionar_pontos(usuario_id, 4500)
        custo_total = 0
        for indice, (_, viagens, custo) in enumerate(TIPOS_PASSAGEM):
            sucesso, saldo = self.repo.resgatar_passagem(usuario_id, indice)
            self.assertTrue(sucesso)
            custo_total += custo
            self.assertEqual(saldo, 5000 - custo_total)
        historico = self.repo.consultar_usuario(usuario_id)["historico"]
        self.assertEqual([t["viagens"] for t in historico], [1, 2, 5])
        self.assertEqual([t["custo"] for t in historico], [587, 1174, 2935])
        self.assertEqual([t["valor"] for t in historico], [5.4, 10.8, 27.0])

    def test_historico_inclui_identificador_e_data_serializavel(self):
        usuario_id = self.repo.criar_usuario("Ana Maria")
        self.repo.adicionar_pontos(usuario_id, 100)
        self.repo.resgatar_passagem(usuario_id, 0)
        registro = self.repo.consultar_usuario(usuario_id)["historico"][0]
        self.assertGreater(registro["id"], 0)
        self.assertIsInstance(registro["data"], str)
        self.assertIsInstance(datetime.fromisoformat(registro["data"]), datetime)
        self.assertEqual(registro, self.repo.listar_usuarios()[0]["historico"][0])
        self.assertIn("/", formatar_data_troca(registro["data"]))
        self.assertEqual(formatar_data_troca(datetime(2026, 11, 1, 10, 20)),
                         "01/11/2026 10:20:00")
        self.assertEqual(formatar_data_troca("valor incorreto"), "Data indisponível")

    def test_relatorio_historico_e_resumo_com_dados_reais(self):
        usuario_id = self.repo.criar_usuario("Ana Maria")
        self.repo.adicionar_pontos(usuario_id, 100)
        self.repo.resgatar_passagem(usuario_id, 0)
        with patch("builtins.input", side_effect=["", ""]), contextlib.redirect_stdout(io.StringIO()) as out:
            historico_trocas(self.repo)
            resumo_sistema(self.repo)
        txt = out.getvalue()
        self.assertIn("Resgate #", txt)
        self.assertIn("Total de viagens resgatadas: 1", txt)
        self.assertIn("Valor total resgatado: R$ 5,40", txt)
        self.assertIn("Total de pontos: 13", txt)

    def test_credito_que_ultrapassa_capacidade_preserva_saldo(self):
        usuario_id = self.repo.criar_usuario("Ana Maria")
        self.repo.alterar_pontos(usuario_id, MAX_PONTOS)
        with self.assertRaisesRegex(ValueError, "ultrapassaria"):
            self.repo.adicionar_pontos(usuario_id, 1)
        self.assertEqual(self.repo.consultar_usuario(usuario_id)["pontos"], MAX_PONTOS)
        self.assertEqual(self.repo.consultar_usuario(usuario_id)["historico"], [])

    def test_validacoes_limites_e_tipos(self):
        self.assertEqual(validar_saldo(MAX_PONTOS), MAX_PONTOS)
        self.assertEqual(validar_saldo(0), 0)
        self.assertEqual(validar_credito(1), 1)
        self.assertEqual(validar_nome_usuario("  Ana Maria  "), "Ana Maria")
        self.assertEqual(validar_nome_usuario("A" * MAX_CARACTERES_NOME),
                         "A" * MAX_CARACTERES_NOME)
        for invalido in (-1, MAX_PONTOS + 1, 1.3, True):
            with self.subTest(saldo=invalido), self.assertRaises(ValueError):
                validar_saldo(invalido)
        for invalido in (0, -1, MAX_PONTOS + 1, True):
            with self.subTest(credito=invalido), self.assertRaises(ValueError):
                validar_credito(invalido)
        for invalido in (None, 12, "", "AB", "A" * 121):
            with self.subTest(nome=invalido), self.assertRaises(ValueError):
                validar_nome_usuario(invalido)
        for invalido in (-1, len(TIPOS_PASSAGEM), True, 1.0):
            with self.subTest(indice=invalido), self.assertRaises(ValueError):
                validar_indice_passagem(invalido)
        usuario_id = self.repo.criar_usuario("Ana Maria")
        with self.assertRaises(ValueError):
            self.repo.alterar_pontos(usuario_id, MAX_PONTOS + 1)
        self.assertEqual(self.repo.consultar_usuario(usuario_id)["pontos"], 500)
        with patch("builtins.input", side_effect=["A" * 121, "Ana"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(validar_nome(), "Ana")

    def test_nao_gera_troca_sem_saldo_suficiente(self):
        usuario_id = self.repo.criar_usuario("Ana Maria")
        self.assertEqual(self.repo.resgatar_passagem(usuario_id, 0), (False, 500))
        self.assertEqual(self.repo.consultar_usuario(usuario_id)["historico"], [])
        self.assertEqual(self.repo.resgatar_passagem(999, 0), (False, None))
        self.assertIsNone(self.repo.adicionar_pontos(999, 2))

    def test_rollback_se_registro_de_troca_falhar(self):
        usuario_id = self.repo.criar_usuario("Ana Maria")
        self.repo.adicionar_pontos(usuario_id, 100)
        self.conexao.falha_na_troca = True
        with self.assertRaises(ErroBanco):
            self.repo.resgatar_passagem(usuario_id, 0)
        self.conexao.falha_na_troca = False
        dados = self.repo.consultar_usuario(usuario_id)
        self.assertEqual(dados["pontos"], 600)
        self.assertEqual(dados["historico"], [])

    def test_erro_de_negocio_eh_mostrado_sem_fechar_programa(self):
        from zyra.cli import app as main
        entradas = ["", "1", "1", "Ana Maria", "", "4", "1", "2", str(MAX_PONTOS + 1), "0", "0"]
        # Após o erro o menu principal reaparece; o submenu do CRUD foi encerrado pela exceção.
        with (patch("zyra.cli.app.conectar", return_value=self.conexao),
              patch("builtins.input", side_effect=entradas),
              contextlib.redirect_stdout(io.StringIO()) as out):
            main.main()
        self.assertIn("Operação inválida", out.getvalue())
        self.assertIn("Programa finalizado", out.getvalue())


if __name__ == "__main__":
    unittest.main()
