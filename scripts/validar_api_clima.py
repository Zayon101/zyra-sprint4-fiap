"""Teste de acesso HTTP real à Open-Meteo (somente leitura; não usa o Oracle)."""

from zyra.integrations.api_clima import ErroAPI, consultar_clima


def main():
    print("TESTE DA API OPEN-METEO - ZYRA")
    print("Fonte: https://open-meteo.com/en/docs")
    print("Não exige cadastro ou chave e não altera o Oracle.\n")
    try:
        dados = consultar_clima()
    except ErroAPI as erro:
        print(f"[ERRO] {erro}")
        return 1
    print("[OK] Requisição HTTP e JSON processados.")
    print(f"[OK] Local: {dados['cidade']}")
    print(f"[OK] Temperatura: {dados['atual']['temperatura']:.1f} °C")
    print(f"[OK] Condição: {dados['atual']['descricao']}")
    print(f"[OK] Previsão: {len(dados['previsao'])} dia(s).")
    print("\nEtapa 6 validada com consulta real à Open-Meteo!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
