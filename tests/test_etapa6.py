"""Testes da Open-Meteo com requisições simuladas, sem acesso à internet/Oracle."""

import contextlib
import io
import unittest
from unittest.mock import Mock, patch

import requests

from api_clima import (
    CatalogoClima, ErroAPI, PARAMETROS, URL_PREVISAO,
    consultar_clima, descrever_tempo, processar_resposta,
)
from clima import menu_clima, mostrar_clima_atual, mostrar_previsao
from tests.oracle_simulado import ConexaoSimulada


DADOS = {
    "latitude": -23.5,
    "longitude": -46.6,
    "timezone": "America/Sao_Paulo",
    "current": {
        "time": "2026-11-01T10:15", "temperature_2m": 23.6,
        "apparent_temperature": 25.4, "relative_humidity_2m": 82,
        "precipitation": 0.1, "weather_code": 3, "wind_speed_10m": 10.5,
    },
    "daily": {
        "time": ["2026-11-01", "2026-11-02", "2026-11-03"],
        "temperature_2m_max": [26.3, 25.2, 27.0],
        "temperature_2m_min": [18.1, 17.2, 19.0],
        "precipitation_probability_max": [80, 60, 10],
        "precipitation_sum": [5.4, 2.0, 0.0],
        "weather_code": [63, 2, 1],
    },
}


def resposta_http(status=200, dados=None):
    resposta = Mock()
    resposta.status_code = status
    resposta.json.return_value = DADOS if dados is None else dados
    return resposta


class TestesAPIOpenMeteo(unittest.TestCase):
    def test_processar_resposta_basica(self):
        resultado = processar_resposta(DADOS)
        self.assertEqual(resultado["cidade"], "São Paulo")
        self.assertEqual(resultado["atual"]["temperatura"], 23.6)
        self.assertEqual(resultado["atual"]["descricao"], "Encoberto")
        self.assertEqual(len(resultado["previsao"]), 3)
        self.assertEqual(resultado["previsao"][0]["probabilidade_chuva"], 80)

    def test_descricao_codigo_desconhecido(self):
        self.assertEqual(descrever_tempo(999), "Condição não identificada")

    def test_processar_rejeita_json_sem_current(self):
        with self.assertRaisesRegex(ErroAPI, "current"):
            processar_resposta({"daily": DADOS["daily"]})

    def test_processar_rejeita_json_sem_daily(self):
        with self.assertRaisesRegex(ErroAPI, "daily"):
            processar_resposta({"current": DADOS["current"]})

    def test_processar_rejeita_lista_diaria_incompleta(self):
        from copy import deepcopy
        dados = deepcopy(DADOS)
        dados["daily"].pop("precipitation_sum")
        with self.assertRaisesRegex(ErroAPI, "incompleta"):
            processar_resposta(dados)

    def test_processar_rejeita_tamanhos_desiguais(self):
        from copy import deepcopy
        dados = deepcopy(DADOS)
        dados["daily"]["weather_code"].pop()
        with self.assertRaisesRegex(ErroAPI, "tamanhos"):
            processar_resposta(dados)

    def test_processar_rejeita_previsao_vazia(self):
        dados = {"current": DADOS["current"], "daily": {campo: [] for campo in DADOS["daily"]}}
        with self.assertRaisesRegex(ErroAPI, "tamanhos"):
            processar_resposta(dados)

    def test_processar_rejeita_umidade_fora_do_intervalo(self):
        from copy import deepcopy
        dados = deepcopy(DADOS)
        dados["current"]["relative_humidity_2m"] = 101
        with self.assertRaisesRegex(ErroAPI, "fora do intervalo"):
            processar_resposta(dados)

    def test_processar_rejeita_nan(self):
        from copy import deepcopy
        dados = deepcopy(DADOS)
        dados["current"]["temperature_2m"] = float("nan")
        with self.assertRaisesRegex(ErroAPI, "inválido"):
            processar_resposta(dados)

    def test_processar_rejeita_bool_como_numero(self):
        from copy import deepcopy
        dados = deepcopy(DADOS)
        dados["current"]["temperature_2m"] = True
        with self.assertRaises(ErroAPI):
            processar_resposta(dados)

    def test_processar_rejeita_data_invalida(self):
        from copy import deepcopy
        dados = deepcopy(DADOS)
        dados["daily"]["time"][0] = "ontem"
        with self.assertRaises(ErroAPI):
            processar_resposta(dados)

    def test_processar_aceita_opcionais_nulos(self):
        from copy import deepcopy
        dados = deepcopy(DADOS)
        dados["current"]["apparent_temperature"] = None
        dados["daily"]["precipitation_probability_max"][0] = None
        resultado = processar_resposta(dados)
        self.assertIsNone(resultado["atual"]["sensacao_termica"])
        self.assertIsNone(resultado["previsao"][0]["probabilidade_chuva"])

    def test_requisicao_get_sem_chave(self):
        cliente = Mock(return_value=resposta_http())
        resultado = consultar_clima(requisicao=cliente)
        self.assertEqual(resultado["cidade"], "São Paulo")
        args, kwargs = cliente.call_args
        self.assertEqual(args[0], URL_PREVISAO)
        self.assertEqual(kwargs["params"], PARAMETROS)
        self.assertEqual(kwargs["params"]["timezone"], "America/Sao_Paulo")
        self.assertNotIn("Authorization", kwargs["headers"])
        self.assertIn("timeout", kwargs)

    def test_requisicao_429(self):
        with self.assertRaisesRegex(ErroAPI, "429"):
            consultar_clima(requisicao=Mock(return_value=resposta_http(429)))

    def test_requisicao_503(self):
        with self.assertRaisesRegex(ErroAPI, "503"):
            consultar_clima(requisicao=Mock(return_value=resposta_http(503)))

    def test_requisicao_400(self):
        with self.assertRaisesRegex(ErroAPI, "400"):
            consultar_clima(requisicao=Mock(return_value=resposta_http(400)))

    def test_requisicao_timeout(self):
        with self.assertRaisesRegex(ErroAPI, "Tempo de espera"):
            consultar_clima(requisicao=Mock(side_effect=requests.Timeout("excedido")))

    def test_requisicao_conexao(self):
        with self.assertRaisesRegex(ErroAPI, "Não foi possível conectar"):
            consultar_clima(requisicao=Mock(side_effect=requests.ConnectionError("falha")))

    def test_requisicao_json_invalido(self):
        resp = resposta_http()
        resp.json.side_effect = ValueError("invalido")
        with self.assertRaisesRegex(ErroAPI, "JSON válido"):
            consultar_clima(requisicao=Mock(return_value=resp))

    def test_cache_reutiliza_dados_no_menu(self):
        consulta = Mock(return_value=processar_resposta(DADOS))
        catalogo = CatalogoClima(consultar=consulta, relogio=lambda: 10)
        self.assertEqual(catalogo.obter(), catalogo.obter())
        self.assertEqual(consulta.call_count, 1)

    def test_cache_atualizacao_antes_5_minutos(self):
        consulta = Mock(return_value=processar_resposta(DADOS))
        catalogo = CatalogoClima(consultar=consulta, relogio=lambda: 10)
        catalogo.obter()
        catalogo.obter(atualizar=True)
        self.assertEqual(consulta.call_count, 1)
        self.assertEqual(catalogo.segundos_para_atualizar(), 300)

    def test_cache_atualizacao_depois_5_minutos(self):
        consulta = Mock(return_value=processar_resposta(DADOS))
        tempo = [0]
        catalogo = CatalogoClima(consultar=consulta, relogio=lambda: tempo[0])
        catalogo.obter()
        tempo[0] = 301
        catalogo.obter(atualizar=True)
        self.assertEqual(consulta.call_count, 2)

    def test_cache_falha_preserva_valores_antigos(self):
        consulta = Mock(side_effect=[processar_resposta(DADOS), ErroAPI("falha")])
        tempo = [0]
        catalogo = CatalogoClima(consultar=consulta, relogio=lambda: tempo[0])
        anterior = catalogo.obter()
        tempo[0] = 301
        with self.assertRaises(ErroAPI):
            catalogo.obter(atualizar=True)
        self.assertIs(catalogo.obter(), anterior)

    def test_exibir_clima_atual(self):
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            mostrar_clima_atual(processar_resposta(DADOS))
        self.assertIn("23,6 °C", saida.getvalue())
        self.assertIn("São Paulo", saida.getvalue())

    def test_exibir_previsao(self):
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            mostrar_previsao(processar_resposta(DADOS))
        self.assertIn("80 %", saida.getvalue())
        self.assertIn("03/11/2026", saida.getvalue())

    def test_menu_consulta_e_volta(self):
        catalogo = CatalogoClima(consultar=Mock(return_value=processar_resposta(DADOS)))
        with patch("builtins.input", side_effect=["1", "", "2", "", "0"]), contextlib.redirect_stdout(io.StringIO()) as saida:
            menu_clima(catalogo)
        self.assertIn("Temperatura", saida.getvalue())
        self.assertIn("PREVISÃO", saida.getvalue())
        self.assertIn("Voltando ao menu principal", saida.getvalue())

    def test_menu_erro_retorna_sem_travar(self):
        catalogo = CatalogoClima(consultar=Mock(side_effect=ErroAPI("offline")))
        with patch("builtins.input", side_effect=["1", "", "0"]), contextlib.redirect_stdout(io.StringIO()) as saida:
            menu_clima(catalogo)
        self.assertIn("offline", saida.getvalue())
        self.assertIn("Voltando ao menu principal", saida.getvalue())

    def test_menu_atualizacao_bloqueada(self):
        catalogo = CatalogoClima(consultar=Mock(return_value=processar_resposta(DADOS)), relogio=lambda: 20)
        with patch("builtins.input", side_effect=["1", "", "3", "", "0"]), contextlib.redirect_stdout(io.StringIO()) as saida:
            menu_clima(catalogo)
        self.assertIn("Dados em cache", saida.getvalue())

    def test_integracao_menu_principal_nao_modifica_oracle(self):
        import main
        conexao = ConexaoSimulada()
        catalogo = CatalogoClima(consultar=Mock(return_value=processar_resposta(DADOS)))
        with (patch("main.conectar", return_value=conexao),
              patch("main.CatalogoClima", return_value=catalogo),
              patch("builtins.input", side_effect=["", "6", "1", "", "0", "0"]),
              contextlib.redirect_stdout(io.StringIO()) as saida):
            main.main()
        self.assertEqual(conexao.commits, 0)
        self.assertTrue(conexao.fechada)
        self.assertIn("Condições para sua viagem", saida.getvalue())
        self.assertIn("Programa finalizado", saida.getvalue())

    def test_validador_com_requisicao_simulada(self):
        from validar_api_clima import main as validar
        with patch("validar_api_clima.consultar_clima", return_value=processar_resposta(DADOS)), contextlib.redirect_stdout(io.StringIO()) as saida:
            self.assertEqual(validar(), 0)
        self.assertIn("Etapa 6 validada", saida.getvalue())

    def test_validador_reporta_erro(self):
        from validar_api_clima import main as validar
        with patch("validar_api_clima.consultar_clima", side_effect=ErroAPI("erro de rede")), contextlib.redirect_stdout(io.StringIO()) as saida:
            self.assertEqual(validar(), 1)
        self.assertIn("erro de rede", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
