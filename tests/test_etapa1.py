"""Testes de regressão das regras de negócio e importação do projeto."""

import contextlib
import importlib
import io
import unittest
from unittest.mock import patch

import constantes
from utils import buscar_indice_por_id, formatar_reais, gerar_id
from usuarios import alterar_usuario, criar_usuario, excluir_usuario, inserir_usuario
from operacoes import adicionar_pontos, trocar_pontos_por_passagem


class TestesEtapa1(unittest.TestCase):
    def test_importar_modulo_nao_inicia_interface(self):
        with patch("builtins.input", side_effect=AssertionError("Não deveria solicitar entrada")):
            with contextlib.redirect_stdout(io.StringIO()) as saida:
                importlib.reload(importlib.import_module("main"))
        self.assertEqual(saida.getvalue(), "")

    def test_constantes_e_formatacao(self):
        self.assertEqual(constantes.BONUS_CADASTRO, 500)
        self.assertEqual(constantes.PONTOS_POR_PASSAGEM, 587)
        self.assertEqual(formatar_reais(5.4), "R$ 5,40")

    def test_cadastro_consulta_e_ids(self):
        usuarios = []
        with patch("builtins.input", return_value="Ana Lima"):
            with contextlib.redirect_stdout(io.StringIO()):
                usuario = criar_usuario(gerar_id(usuarios))
                ok = inserir_usuario(usuarios, usuario)
        self.assertTrue(ok)
        self.assertEqual(usuarios[0]["pontos"], 500)
        self.assertEqual(buscar_indice_por_id(usuarios, 1), 0)
        self.assertEqual(gerar_id(usuarios), 2)

    def test_alterar_e_excluir(self):
        usuarios = [{"id": 1, "nome": "Ana Lima", "pontos": 500, "historico": []}]
        with patch("builtins.input", side_effect=["1", "1", "Ana Maria", ""]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(alterar_usuario(usuarios))
        self.assertEqual(usuarios[0]["nome"], "Ana Maria")
        with patch("builtins.input", side_effect=["1", "1", ""]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(excluir_usuario(usuarios))
        self.assertEqual(usuarios, [])

    def test_pontos_e_troca(self):
        usuario = {"id": 1, "nome": "Ana Lima", "pontos": 500, "historico": []}
        with patch("builtins.input", side_effect=["100", ""]):
            with contextlib.redirect_stdout(io.StringIO()):
                usuario = adicionar_pontos(usuario)
        self.assertEqual(usuario["pontos"], 600)
        with patch("builtins.input", side_effect=["1", ""]):
            with contextlib.redirect_stdout(io.StringIO()):
                usuario = trocar_pontos_por_passagem(usuario)
        self.assertEqual(usuario["pontos"], 13)
        self.assertEqual(usuario["historico"][0]["custo"], 587)
        with patch("builtins.input", side_effect=["1", ""]):
            with contextlib.redirect_stdout(io.StringIO()):
                resultado = trocar_pontos_por_passagem(usuario)
        self.assertEqual(resultado, usuario)


if __name__ == "__main__":
    unittest.main()
