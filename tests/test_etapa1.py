"""Regressões ainda aplicáveis das regras iniciais da Sprint 3."""

import contextlib
import importlib
import io
import unittest
from unittest.mock import patch

from zyra.core import constantes
from zyra.cli.utils import formatar_reais, validar_nome, validar_numero


class TestesEtapa1(unittest.TestCase):
    def test_importar_main_nao_inicia_interface(self):
        with patch("builtins.input", side_effect=AssertionError("Não deve iniciar")):
            with contextlib.redirect_stdout(io.StringIO()) as saida:
                importlib.reload(importlib.import_module("main"))
        self.assertEqual(saida.getvalue(), "")

    def test_constantes_sprint3_preservadas(self):
        self.assertEqual(constantes.BONUS_CADASTRO, 500)
        self.assertEqual(constantes.PONTOS_POR_PASSAGEM, 587)
        self.assertEqual(constantes.TIPOS_PASSAGEM[2][2], 2935)
        self.assertEqual(formatar_reais(5.4), "R$ 5,40")

    def test_validar_nome_rejeita_numero_e_curto(self):
        with (patch("builtins.input", side_effect=["Al", "Ana1", "Ana Clara"]),
              contextlib.redirect_stdout(io.StringIO())):
            self.assertEqual(validar_nome(), "Ana Clara")

    def test_validar_numero_rejeita_letras(self):
        with (patch("builtins.input", side_effect=["abc", "12"]),
              contextlib.redirect_stdout(io.StringIO())):
            self.assertEqual(validar_numero("Digite:"), 12)

    def test_mostrar_passagens_mantem_custos(self):
        from zyra.cli.operacoes import mostrar_passagens
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            mostrar_passagens()
        self.assertIn("587 pontos", saida.getvalue())
        self.assertIn("1174 pontos", saida.getvalue())
        self.assertIn("2935 pontos", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
