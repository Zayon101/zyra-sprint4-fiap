"""Menu de informações meteorológicas para planejamento de viagens do Zyra."""

from datetime import datetime

from api.clima import CatalogoClima, ErroAPI, FONTE
from sistema.utils import pausar, validar_numero


def _formatar_valor(valor, unidade, casas=1):
    """Exibe números com vírgula decimal; preserva ausência de dados."""
    if valor is None:
        return "Não disponível"
    return f"{valor:.{casas}f} {unidade}".replace(".", ",")


def _formatar_data(data, hora=False):
    valor = datetime.fromisoformat(data)
    return valor.strftime("%d/%m/%Y %H:%M" if hora else "%d/%m/%Y")


def mostrar_clima_atual(dados):
    """Exibe a situação meteorológica fornecida pela API."""
    atual = dados["atual"]
    print("\n" + "=" * 52)
    print(f"CONDIÇÕES PARA SUA VIAGEM - {dados['cidade']}".center(52))
    print("=" * 52)
    print(f"Data e hora dos dados: {_formatar_data(atual['horario'], hora=True)}")
    print(f"Condição: {atual['descricao']}")
    print(f"Temperatura: {_formatar_valor(atual['temperatura'], '°C')}")
    print(f"Sensação térmica: {_formatar_valor(atual['sensacao_termica'], '°C')}")
    print(f"Umidade: {_formatar_valor(atual['umidade'], '%', 0)}")
    print(f"Precipitação no intervalo informado: {_formatar_valor(atual['precipitacao'], 'mm')}")
    print(f"Vento: {_formatar_valor(atual['vento'], 'km/h')}")
    print(f"\nFonte: {FONTE}")
    print("Dados meteorológicos modelados: não representam o status do metrô.")


def mostrar_previsao(dados):
    """Mostra previsão diária com temperaturas e chance de chuva."""
    print("\n" + "=" * 52)
    print(f"PREVISÃO PARA OS PRÓXIMOS DIAS - {dados['cidade']}".center(52))
    print("=" * 52)
    for dia in dados["previsao"]:
        print(f"\n{_formatar_data(dia['data'])} | {dia['descricao']}")
        print(f"  Mínima: {_formatar_valor(dia['minima'], '°C')} | Máxima: {_formatar_valor(dia['maxima'], '°C')}")
        print(f"  Probabilidade máxima de chuva: {_formatar_valor(dia['probabilidade_chuva'], '%', 0)}")
        print(f"  Precipitação diária prevista: {_formatar_valor(dia['precipitacao'], 'mm')}")
    print(f"\nFonte: {FONTE}")
    print("Previsões podem mudar; confira novamente antes de viajar.")


def menu_clima(catalogo=None):
    """Navega entre clima atual, previsão e atualização manual do cache."""
    catalogo = catalogo if catalogo is not None else CatalogoClima()
    opcao = -1
    while opcao != 0:
        print("\n" + "=" * 52)
        print("CONDIÇÕES PARA SUA VIAGEM - OPEN-METEO".center(52))
        print("=" * 52)
        print("[1] Consultar condições atuais em São Paulo")
        print("[2] Previsão para os próximos 3 dias")
        print("[3] Atualizar dados (intervalo mínimo de 5 min)")
        print("-" * 52)
        print("[0] Voltar")
        opcao = validar_numero("Escolha uma opção: ")
        if opcao == 0:
            print("\nVoltando ao menu principal...")
            break
        if opcao not in (1, 2, 3):
            print("\nOpção inválida.")
            continue
        try:
            restante = catalogo.segundos_para_atualizar() if opcao == 3 else 0
            dados = catalogo.obter(atualizar=opcao == 3)
            if opcao == 1:
                mostrar_clima_atual(dados)
            elif opcao == 2:
                mostrar_previsao(dados)
            elif restante:
                print(f"\nDados em cache. Nova consulta disponível em aproximadamente {restante} segundos.")
            else:
                print("\n[OK] Informações meteorológicas atualizadas.")
                if catalogo.consultado_em:
                    print(f"Consulta local: {catalogo.consultado_em:%d/%m/%Y %H:%M:%S}")
        except ErroAPI as erro:
            print(f"\nErro ao consultar a Open-Meteo: {erro}")
            print("O Oracle e os demais recursos do Zyra continuam disponíveis.")
        pausar()
