"""Testes locais para configuração, scripts Oracle e regressões da Etapa 2.

Não exigem acesso ao banco real nem instalam dependências externas do Oracle.
"""

import contextlib
import io
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, Mock, patch

import banco
import main
from preparar_banco import ler_instrucoes_sql, preparar_estrutura
from testar_banco import TABELAS_ESPERADAS, verificar_conexao


class TestesEtapa2(unittest.TestCase):
    def configuracao(self, **variacoes):
        dados = {
            "ORACLE_USER": "rm_aluno",
            "ORACLE_PASSWORD": "senha-ficticia",
            "ORACLE_HOST": "host.exemplo",
            "ORACLE_PORT": "1521",
            "ORACLE_SERVICE_NAME": "FIAP_SERVICE",
            "ORACLE_SID": "",
        }
        dados.update(variacoes)
        with patch.dict(os.environ, dados, clear=True), patch("banco.load_dotenv"):
            return banco.carregar_configuracao()

    def test_configuracao_com_nome_de_servico(self):
        conf = self.configuracao()
        self.assertEqual(conf.porta, 1521)
        self.assertEqual(conf.servico, "FIAP_SERVICE")
        self.assertEqual(conf.sid, "")
        self.assertNotIn("senha-ficticia", repr(conf))

    def test_configuracao_com_sid(self):
        conf = self.configuracao(ORACLE_SERVICE_NAME="", ORACLE_SID="ORCL")
        self.assertEqual(conf.sid, "ORCL")
        self.assertEqual(conf.servico, "")

    def test_erro_sem_identificador_ou_com_dois(self):
        with self.assertRaisesRegex(ValueError, "exatamente um"):
            self.configuracao(ORACLE_SERVICE_NAME="", ORACLE_SID="")
        with self.assertRaisesRegex(ValueError, "exatamente um"):
            self.configuracao(ORACLE_SERVICE_NAME="FIAP", ORACLE_SID="ORCL")

    def test_erro_credencial_ausente(self):
        with self.assertRaisesRegex(ValueError, "ORACLE_PASSWORD"):
            self.configuracao(ORACLE_PASSWORD="")

    def test_porta_invalida(self):
        for porta in ("abc", "0", "65536"):
            with self.subTest(porta=porta), self.assertRaises(ValueError):
                self.configuracao(ORACLE_PORT=porta)

    def test_conexao_passa_parametros_corretos_ao_driver(self):
        driver = types.ModuleType("oracledb")
        driver.connect = Mock(return_value="conexao_fake")
        with patch.dict(sys.modules, {"oracledb": driver}):
            conexao = banco.conectar(self.configuracao())
        self.assertEqual(conexao, "conexao_fake")
        driver.connect.assert_called_once_with(
            user="rm_aluno",
            password="senha-ficticia",
            host="host.exemplo",
            port=1521,
            service_name="FIAP_SERVICE",
        )

        driver.connect.reset_mock()
        with patch.dict(sys.modules, {"oracledb": driver}):
            banco.conectar(self.configuracao(ORACLE_SERVICE_NAME="", ORACLE_SID="ORCL"))
        self.assertEqual(driver.connect.call_args.kwargs["sid"], "ORCL")
        self.assertNotIn("service_name", driver.connect.call_args.kwargs)

    def test_sql_possui_tabelas_e_indice_com_relacionamento(self):
        sql = ler_instrucoes_sql()
        self.assertEqual(
            [(tipo, nome) for tipo, nome, _ in sql],
            [("TABLE", "ZYRA_USUARIOS"), ("TABLE", "ZYRA_TROCAS"),
             ("INDEX", "IX_ZYRA_TROCAS_USUARIO")],
        )
        self.assertIn("ON DELETE CASCADE", sql[1][2])
        self.assertIn("FOREIGN KEY", sql[1][2])
        self.assertIn("DEFAULT 500", sql[0][2])

    def test_sql_recusa_comando_nao_permitido(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "outro.sql"
            caminho.write_text("DROP TABLE ZYRA_USUARIOS;", encoding="utf-8")
            with self.assertRaises(ValueError):
                ler_instrucoes_sql(caminho)

    def test_preparacao_cria_apenas_objetos_que_faltam(self):
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.fetchone.side_effect = [None, None, None]
        conexao = Mock()
        conexao.cursor.return_value = cursor
        with contextlib.redirect_stdout(io.StringIO()):
            criados = preparar_estrutura(conexao)
        self.assertEqual(
            criados, ["ZYRA_USUARIOS", "ZYRA_TROCAS", "IX_ZYRA_TROCAS_USUARIO"]
        )
        self.assertEqual(cursor.execute.call_count, 6)  # 3 consultas + 3 CREATE

        cursor.reset_mock()
        cursor.fetchone.side_effect = [(1,), (1,), (1,)]
        with contextlib.redirect_stdout(io.StringIO()):
            criados = preparar_estrutura(conexao)
        self.assertEqual(criados, [])
        self.assertEqual(cursor.execute.call_count, 3)  # só consultas

    def test_consulta_de_diagnostico_e_somente_leitura(self):
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.fetchone.return_value = ("RM_ALUNO",)
        cursor.fetchall.return_value = [("ZYRA_USUARIOS",), ("ZYRA_TROCAS",)]
        conexao = Mock()
        conexao.cursor.return_value = cursor
        usuario, tabelas = verificar_conexao(conexao)
        self.assertEqual(usuario, "RM_ALUNO")
        self.assertEqual(tabelas, TABELAS_ESPERADAS)
        consultas = [chamada.args[0] for chamada in cursor.execute.call_args_list]
        self.assertEqual(len(consultas), 2)
        self.assertTrue(all(sql.startswith("SELECT") for sql in consultas))

    def test_menu_historico_vazio_pausa_sem_name_error(self):
        with (patch("main.carregar_dados", return_value=[]),
              patch("main.salvar_dados"),
              patch("main.exibir_boas_vindas"),
              patch("main.exibir_menu"),
              patch("main.escolher_usuario", return_value=None),
              patch("main.pausar") as pausar,
              patch("builtins.input", side_effect=["3", "0"]),
              contextlib.redirect_stdout(io.StringIO())):
            main.main()
        pausar.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
