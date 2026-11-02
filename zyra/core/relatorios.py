"""Cálculos de relatórios reutilizados pelo terminal e pela exportação JSON."""

from decimal import Decimal, ROUND_HALF_UP

from zyra.core.constantes import PONTOS_POR_PASSAGEM, VALOR_PASSAGEM


CENTAVOS = Decimal("0.01")


def calcular_resumo(usuarios):
    """Calcula indicadores a partir dos registros consultados no Oracle.

    O valor equivalente dos pontos segue a regra simulada do Zyra.
    Valores monetários são arredondados para centavos antes da conversão
    para números JSON, evitando somas com erros de ponto flutuante.
    """
    historicos = [troca for usuario in usuarios for troca in usuario["historico"]]
    total_pontos = sum(usuario["pontos"] for usuario in usuarios)
    valor_saldo = (
        Decimal(total_pontos) * Decimal(str(VALOR_PASSAGEM))
        / Decimal(PONTOS_POR_PASSAGEM)
    ).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    valor_resgatado = sum(
        (Decimal(str(troca["valor"])) for troca in historicos), Decimal("0")
    ).quantize(CENTAVOS, rounding=ROUND_HALF_UP)

    return {
        "total_usuarios": len(usuarios),
        "total_pontos": total_pontos,
        "valor_total_saldo_reais": float(valor_saldo),
        "total_trocas": len(historicos),
        "total_viagens": sum(troca["viagens"] for troca in historicos),
        "valor_total_resgatado_reais": float(valor_resgatado),
    }
