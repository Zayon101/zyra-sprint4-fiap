"""Consulta pública de clima em São Paulo para planejamento de viagens no Zyra.

Fonte: https://open-meteo.com/en/docs
Não exige cadastro, chave, nem consulta/modificação ao banco Oracle.
"""

import math
import time
from datetime import datetime

import requests


URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"
FONTE = "Open-Meteo (https://open-meteo.com/)"
CIDADE = "São Paulo"
INTERVALO_ATUALIZACAO = 300  # 5 minutos
PARAMETROS = {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "current": "temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,weather_code",
    "timezone": "America/Sao_Paulo",
    "forecast_days": 3,
}

DESCRICOES_TEMPO = {
    0: "Céu limpo", 1: "Predominantemente limpo", 2: "Parcialmente nublado",
    3: "Encoberto", 45: "Nevoeiro", 48: "Nevoeiro com geada",
    51: "Garoa fraca", 53: "Garoa moderada", 55: "Garoa intensa",
    56: "Garoa congelante fraca", 57: "Garoa congelante intensa",
    61: "Chuva fraca", 63: "Chuva moderada", 65: "Chuva forte",
    66: "Chuva congelante fraca", 67: "Chuva congelante forte",
    71: "Neve fraca", 73: "Neve moderada", 75: "Neve forte",
    77: "Grãos de neve", 80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva moderadas", 82: "Pancadas de chuva fortes",
    85: "Pancadas de neve fracas", 86: "Pancadas de neve fortes",
    95: "Trovoadas", 96: "Trovoadas com granizo fraco",
    97: "Trovoadas fortes", 99: "Trovoadas com granizo forte",
}


class ErroAPI(Exception):
    """Falha de rede, HTTP ou formato de dados retornados pela Open-Meteo."""


def descrever_tempo(codigo):
    """Traduz códigos meteorológicos WMO para descrições em português."""
    return DESCRICOES_TEMPO.get(codigo, "Condição não identificada")


def _numero(valor, campo, obrigatorio=True, minimo=None, maximo=None):
    """Valida um valor numérico da API (incluindo limites quando definidos)."""
    if valor is None and not obrigatorio:
        return None
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
        raise ErroAPI(f"Resposta inesperada da Open-Meteo: '{campo}' inválido.")
    if minimo is not None and valor < minimo or maximo is not None and valor > maximo:
        raise ErroAPI(f"Resposta inesperada da Open-Meteo: '{campo}' fora do intervalo.")
    return valor


def _codigo(valor, campo):
    if type(valor) is not int or valor < 0:
        raise ErroAPI(f"Resposta inesperada da Open-Meteo: '{campo}' inválido.")
    return valor


def _data(valor, campo):
    if not isinstance(valor, str):
        raise ErroAPI(f"Resposta inesperada da Open-Meteo: '{campo}' inválido.")
    try:
        datetime.fromisoformat(valor)
    except ValueError as erro:
        raise ErroAPI(f"Resposta inesperada da Open-Meteo: '{campo}' inválido.") from erro
    return valor


def processar_resposta(dados):
    """Valida e normaliza condições atuais e previsão diária retornadas pela API."""
    if not isinstance(dados, dict) or not isinstance(dados.get("current"), dict) or not isinstance(dados.get("daily"), dict):
        raise ErroAPI("A Open-Meteo retornou um JSON sem os campos 'current' e 'daily'.")
    atual = dados["current"]
    diarios = dados["daily"]
    campos = (
        "time", "temperature_2m_max", "temperature_2m_min",
        "precipitation_probability_max", "precipitation_sum", "weather_code",
    )
    if any(not isinstance(diarios.get(campo), list) for campo in campos):
        raise ErroAPI("A previsão da Open-Meteo está incompleta ou inválida.")
    total = len(diarios["time"])
    if total == 0 or any(len(diarios[campo]) != total for campo in campos):
        raise ErroAPI("Os campos da previsão da Open-Meteo possuem tamanhos inconsistentes.")

    resultado = {
        "cidade": CIDADE,
        "atual": {
            "horario": _data(atual.get("time"), "current.time"),
            "temperatura": _numero(atual.get("temperature_2m"), "current.temperature_2m"),
            "sensacao_termica": _numero(atual.get("apparent_temperature"), "current.apparent_temperature", obrigatorio=False),
            "umidade": _numero(atual.get("relative_humidity_2m"), "current.relative_humidity_2m", obrigatorio=False, minimo=0, maximo=100),
            "precipitacao": _numero(atual.get("precipitation"), "current.precipitation", minimo=0),
            "vento": _numero(atual.get("wind_speed_10m"), "current.wind_speed_10m", obrigatorio=False, minimo=0),
            "codigo_tempo": _codigo(atual.get("weather_code"), "current.weather_code"),
        },
        "previsao": [],
    }
    resultado["atual"]["descricao"] = descrever_tempo(resultado["atual"]["codigo_tempo"])

    for indice in range(total):
        def valor(campo):
            return diarios[campo][indice]
        codigo = _codigo(valor("weather_code"), "daily.weather_code")
        resultado["previsao"].append({
            "data": _data(valor("time"), "daily.time"),
            "maxima": _numero(valor("temperature_2m_max"), "daily.temperature_2m_max"),
            "minima": _numero(valor("temperature_2m_min"), "daily.temperature_2m_min"),
            "probabilidade_chuva": _numero(valor("precipitation_probability_max"), "daily.precipitation_probability_max", obrigatorio=False, minimo=0, maximo=100),
            "precipitacao": _numero(valor("precipitation_sum"), "daily.precipitation_sum", obrigatorio=False, minimo=0),
            "codigo_tempo": codigo,
            "descricao": descrever_tempo(codigo),
        })
    return resultado


def consultar_clima(requisicao=None):
    """Executa GET público à Open-Meteo e retorna dados normalizados."""
    cliente = requisicao if requisicao is not None else requests.get
    try:
        resposta = cliente(
            URL_PREVISAO,
            params=PARAMETROS.copy(),
            headers={"Accept": "application/json", "User-Agent": "Zyra-FIAP-Sprint4/1.0"},
            timeout=(5, 15),
        )
        if resposta.status_code != 200:
            if resposta.status_code == 429:
                raise ErroAPI("HTTP 429: limite de consultas da Open-Meteo excedido. Aguarde antes de tentar novamente.")
            if resposta.status_code in (502, 503, 504):
                raise ErroAPI(f"HTTP {resposta.status_code}: serviço Open-Meteo temporariamente indisponível.")
            raise ErroAPI(f"A API Open-Meteo retornou HTTP {resposta.status_code}.")
        dados = resposta.json()
    except requests.Timeout as erro:
        raise ErroAPI("Tempo de espera excedido ao consultar a Open-Meteo. Verifique a conexão.") from erro
    except requests.ConnectionError as erro:
        raise ErroAPI("Não foi possível conectar à Open-Meteo. Verifique o acesso à internet.") from erro
    except requests.RequestException as erro:
        raise ErroAPI("Falha de comunicação HTTP com a Open-Meteo.") from erro
    except ValueError as erro:
        raise ErroAPI("A Open-Meteo não retornou um JSON válido.") from erro
    return processar_resposta(dados)


class CatalogoClima:
    """Cache em memória para não repetir a mesma consulta a cada opção do menu."""

    def __init__(self, consultar=None, relogio=None):
        self._consultar = consultar if consultar is not None else consultar_clima
        self._relogio = relogio if relogio is not None else time.monotonic
        self._dados = None
        self._instante = None
        self.consultado_em = None

    def obter(self, atualizar=False):
        """Carrega na primeira consulta; atualiza sob pedido após cinco minutos."""
        agora = self._relogio()
        permitido = self._instante is None or agora - self._instante >= INTERVALO_ATUALIZACAO
        if self._dados is None or (atualizar and permitido):
            novos_dados = self._consultar()
            self._dados = novos_dados
            self._instante = self._relogio()
            self.consultado_em = datetime.now().astimezone()
        return self._dados

    def segundos_para_atualizar(self):
        """Informa quando uma nova consulta manual será permitida."""
        if self._instante is None:
            return 0
        return max(0, math.ceil(INTERVALO_ATUALIZACAO - (self._relogio() - self._instante)))
