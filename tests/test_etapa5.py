"""Testes de exportação JSON com Oracle simulado e menus reais."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from exportacao import exportar_consulta, montar_consulta
from menus import menu_exportacao
from relatorios import calcular_resumo
from repositorio import ErroBanco, RepositorioOracle
from tests.oracle_simulado import ConexaoSimulada


class TestesEtapa5(unittest.TestCase):
    def setUp(self):
        self.conexao = ConexaoSimulada()
        self.repo = RepositorioOracle(self.conexao)
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()
        if not self.conexao.fechada:
            self.conexao.close()

    def ler_exportacao(self, tipo, id_usuario=None):
        caminho = exportar_consulta(self.repo, tipo, id_usuario, self.pasta)
        return caminho, json.loads(caminho.read_text(encoding="utf-8"))

    def test_exportar_todos_usuarios_quando_banco_esta_vazio(self):
        caminho, dados = self.ler_exportacao("usuarios")
        self.assertTrue(caminho.is_file())
        self.assertEqual(dados["tipo"], "usuarios")
        self.assertEqual(dados["total"], 0)
        self.assertEqual(dados["usuarios"], [])
        self.assertIn("exportado_em", dados)

    def test_exportar_todos_preserva_acentos_e_historico(self):
        id_usuario = self.repo.criar_usuario("João Cézar")
        self.repo.adicionar_pontos(id_usuario, 100)
        self.repo.resgatar_passagem(id_usuario, 0)
        caminho, dados = self.ler_exportacao("usuarios")
        self.assertEqual(dados["total"], 1)
        self.assertEqual(dados["usuarios"], self.repo.listar_usuarios())
        self.assertIn("João Cézar", caminho.read_text(encoding="utf-8"))
        self.assertEqual(dados["usuarios"][0]["historico"][0]["custo"], 587)
        self.assertEqual(dados["usuarios"][0]["historico"][0]["valor"], 5.4)
        self.assertIn("T", dados["usuarios"][0]["historico"][0]["data"])
        self.assertEqual(dados["usuarios"][0]["pontos"], 13)

    def test_exportar_usuario_por_id_e_preservar_estrutura(self):
        primeiro = self.repo.criar_usuario("Ana Maria")
        segundo = self.repo.criar_usuario("João Souza")
        caminho, dados = self.ler_exportacao("usuario", segundo)
        self.assertIn(f"usuario_{segundo}_", caminho.name)
        self.assertEqual(dados["usuario"]["id"], segundo)
        self.assertEqual(dados["usuario"]["nome"], "João Souza")
        self.assertEqual(dados["usuario"]["historico"], [])
        self.assertNotEqual(dados["usuario"]["id"], primeiro)

    def test_nao_exporta_usuario_inexistente(self):
        self.assertIsNone(exportar_consulta(self.repo, "usuario", 999, self.pasta))
        self.assertIsNone(exportar_consulta(self.repo, "historico", 999, self.pasta))
        self.assertEqual(list(self.pasta.iterdir()), [])

    def test_exportar_historico_vazio_e_preenchido(self):
        id_usuario = self.repo.criar_usuario("Ana Maria")
        _, inicial = self.ler_exportacao("historico", id_usuario)
        self.assertEqual(inicial["total_trocas"], 0)
        self.assertEqual(inicial["trocas"], [])
        self.repo.adicionar_pontos(id_usuario, 100)
        self.repo.resgatar_passagem(id_usuario, 0)
        _, atual = self.ler_exportacao("historico", id_usuario)
        self.assertEqual(atual["total_trocas"], 1)
        self.assertEqual(atual["usuario"]["id"], id_usuario)
        self.assertEqual(atual["trocas"][0]["viagens"], 1)
        self.assertIsInstance(atual["trocas"][0]["id"], int)
        self.assertIn("data", atual["trocas"][0])

    def test_resumo_compartilhado_com_a_tela(self):
        id_usuario = self.repo.criar_usuario("Ana Maria")
        self.repo.criar_usuario("Bia Souza")
        self.repo.adicionar_pontos(id_usuario, 100)
        self.repo.resgatar_passagem(id_usuario, 0)
        _, dados = self.ler_exportacao("resumo")
        indicadores = dados["resumo"]
        self.assertEqual(indicadores, calcular_resumo(self.repo.listar_usuarios()))
        self.assertEqual(indicadores["total_usuarios"], 2)
        self.assertEqual(indicadores["total_pontos"], 513)
        self.assertEqual(indicadores["total_trocas"], 1)
        self.assertEqual(indicadores["total_viagens"], 1)
        self.assertEqual(indicadores["valor_total_resgatado_reais"], 5.4)
        self.assertEqual(indicadores["valor_total_saldo_reais"], 4.72)

    def test_exportacao_nao_gera_commit_nem_modifica_registros(self):
        id_usuario = self.repo.criar_usuario("Ana Maria")
        commits_antes = self.conexao.commits
        dados_antes = self.repo.listar_usuarios()
        for tipo, identificador in (("usuarios", None), ("usuario", id_usuario),
                                    ("historico", id_usuario), ("resumo", None)):
            self.ler_exportacao(tipo, identificador)
        self.assertEqual(self.conexao.commits, commits_antes)
        self.assertEqual(self.repo.listar_usuarios(), dados_antes)

    def test_nao_sobrescreve_arquivo_existente(self):
        self.repo.criar_usuario("Ana Maria")
        with patch("exportacao._nome_arquivo", return_value="fixo.json"):
            primeiro = exportar_consulta(self.repo, "usuarios", pasta_destino=self.pasta)
            conteudo = primeiro.read_bytes()
            with self.assertRaises(FileExistsError):
                exportar_consulta(self.repo, "usuarios", pasta_destino=self.pasta)
            self.assertEqual(primeiro.read_bytes(), conteudo)
            self.assertEqual(len(list(self.pasta.iterdir())), 1)

    def test_falha_na_escrita_remove_arquivo_parcial(self):
        self.repo.criar_usuario("Ana Maria")
        with patch("exportacao.json.dump", side_effect=TypeError("Falha de teste")):
            with self.assertRaises(TypeError):
                exportar_consulta(self.repo, "usuarios", pasta_destino=self.pasta)
        self.assertEqual(list(self.pasta.iterdir()), [])

    def test_parametros_invalidos_nao_criam_arquivos(self):
        for tipo, identificador in (("inexistente", None), ("usuario", -1),
                                    ("historico", True), ("usuario", "1")):
            with self.subTest(tipo=tipo, identificador=identificador):
                with self.assertRaises(ValueError):
                    exportar_consulta(self.repo, tipo, identificador, self.pasta)
        self.assertFalse(any(self.pasta.iterdir()))

    def test_montagem_nao_gera_exportacao_em_disco(self):
        self.repo.criar_usuario("Ana Maria")
        self.assertEqual(montar_consulta(self.repo, "usuarios")["total"], 1)
        self.assertEqual(list(self.pasta.iterdir()), [])

    def test_menu_com_quatro_opcoes_e_retorno(self):
        usuario_id = self.repo.criar_usuario("Ana Maria")
        entradas = ["1", "", "2", str(usuario_id), "", "3", str(usuario_id), "", "4", "", "0"]
        with (patch("menus.exportar_consulta", wraps=exportar_consulta) as exportador,
              patch("exportacao.PASTA_EXPORTACOES", self.pasta),
              patch("builtins.input", side_effect=entradas),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            menu_exportacao(self.repo)
        self.assertEqual(exportador.call_count, 4)
        self.assertEqual(len(list(self.pasta.glob("*.json"))), 4)
        self.assertEqual(saida.getvalue().count("Consulta exportada com sucesso"), 4)

    def test_menu_id_inexistente_e_opcao_invalida(self):
        with (patch("builtins.input", side_effect=["7", "2", "999", "", "0"]),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            menu_exportacao(self.repo)
        self.assertIn("Opção inválida", saida.getvalue())
        self.assertIn("Usuário não encontrado", saida.getvalue())

    def test_menu_trata_falha_gravacao_sem_fechar_submenu(self):
        with (patch("menus.exportar_consulta", side_effect=OSError("disco indisponível")),
              patch("builtins.input", side_effect=["1", "", "0"]),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            menu_exportacao(self.repo)
        self.assertIn("Erro ao criar arquivo JSON", saida.getvalue())
        self.assertIn("Voltando ao menu principal", saida.getvalue())

    def test_integracao_main_menu_exportacao(self):
        import main
        entradas = ["", "5", "1", "", "0", "0"]
        with (patch("main.conectar", return_value=self.conexao),
              patch("exportacao.PASTA_EXPORTACOES", self.pasta),
              patch("builtins.input", side_effect=entradas),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            main.main()
        self.assertIn("Exportar consultas em JSON", saida.getvalue())
        self.assertIn("Consulta exportada com sucesso", saida.getvalue())
        self.assertIn("Programa finalizado", saida.getvalue())
        self.assertEqual(len(list(self.pasta.glob("*.json"))), 1)
        self.assertTrue(self.conexao.fechada)


class TestesValidadorOracleEtapa5(unittest.TestCase):
    """Testa o roteiro de validação real usando uma conexão simulada."""

    def test_validador_sem_cadastros(self):
        from validar_exportacao_oracle import main as validar
        conexao = ConexaoSimulada()
        with (patch("validar_exportacao_oracle.conectar", return_value=conexao),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            resultado = validar()
        self.assertEqual(resultado, 0)
        self.assertIn("[INFO] Sem usuários", saida.getvalue())
        self.assertTrue(conexao.fechada)

    def test_validador_com_cadastros_e_historico(self):
        from validar_exportacao_oracle import main as validar
        conexao = ConexaoSimulada()
        repositorio = RepositorioOracle(conexao)
        usuario_id = repositorio.criar_usuario("Ana Maria")
        repositorio.adicionar_pontos(usuario_id, 100)
        repositorio.resgatar_passagem(usuario_id, 0)
        commits_antes = conexao.commits
        with (patch("validar_exportacao_oracle.conectar", return_value=conexao),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            resultado = validar()
        self.assertEqual(resultado, 0)
        self.assertEqual(commits_antes, conexao.commits)
        self.assertIn("[OK] Exportação individual por ID", saida.getvalue())
        self.assertIn("[OK] Exportação do histórico", saida.getvalue())
        self.assertTrue(conexao.fechada)


if __name__ == "__main__":
    unittest.main()
