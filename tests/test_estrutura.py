"""Verifica a reorganização sem depender do Oracle ou da internet."""

import runpy
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.preparar_banco import ARQUIVO_SQL, ler_instrucoes_sql
from zyra.core.constantes import ARQUIVO_DADOS
from zyra.database.banco import ARQUIVO_AMBIENTE
from zyra.exportacao import PASTA_EXPORTACOES
from zyra.web.servidor import PASTA_PAINEL


RAIZ = Path(__file__).resolve().parents[1]


class TestesEstrutura(unittest.TestCase):
    def test_env_na_raiz_do_projeto(self):
        self.assertEqual(ARQUIVO_AMBIENTE, RAIZ / '.env')
        self.assertTrue((RAIZ / '.env.example').is_file())

    def test_arquivo_legado_esperado_na_raiz(self):
        self.assertEqual(ARQUIVO_DADOS, RAIZ / 'dados_zyra.json')

    def test_exportacoes_na_raiz(self):
        self.assertEqual(PASTA_EXPORTACOES, RAIZ / 'exportacoes')

    def test_ddl_no_diretorio_sql(self):
        self.assertEqual(ARQUIVO_SQL, RAIZ / 'sql' / 'criar_tabelas.sql')
        self.assertEqual(len(ler_instrucoes_sql()), 3)

    def test_painel_web_resolve_arquivos(self):
        self.assertEqual(PASTA_PAINEL, RAIZ / 'examples' / 'painel_web')
        for nome in ('index.html', 'painel.js', 'painel.css'):
            with self.subTest(nome=nome):
                self.assertTrue((PASTA_PAINEL / nome).is_file())

    def test_main_chama_aplicacao_cli(self):
        with patch('zyra.cli.app.main') as iniciar:
            runpy.run_path(str(RAIZ / 'main.py'), run_name='__main__')
        iniciar.assert_called_once_with()

    def test_servidor_chama_aplicacao_http(self):
        with patch('zyra.web.servidor.main') as iniciar:
            runpy.run_path(str(RAIZ / 'servidor_web.py'), run_name='__main__')
        iniciar.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
