"""Aplicação de terminal do Zyra (menus e conexão principal)."""

from zyra.integrations.api_clima import CatalogoClima
from zyra.database.banco import conectar
from zyra.cli.menus import exibir_boas_vindas, exibir_menu, menu_crud, menu_operacoes, menu_exportacao
from zyra.cli.clima import menu_clima
from zyra.cli.operacoes import historico_trocas, resumo_sistema
from zyra.database.repositorio import ErroBanco, RepositorioOracle


def main():
    """Abre uma conexão Oracle e controla os menus até a opção de sair."""
    try:
        conexao = conectar()
    except Exception as erro:
        print(f"\nNão foi possível conectar ao Oracle: {erro}")
        print("Verifique o .env, a rede da FIAP e execute python -m scripts.testar_banco.")
        return

    try:
        repositorio = RepositorioOracle(conexao)
        catalogo_clima = CatalogoClima()
        exibir_boas_vindas()
        opcao = -1
        while opcao != 0:
            exibir_menu()
            try:
                opcao = int(input("Escolha uma opção: "))
            except ValueError:
                print("\nErro: digite apenas números.")
                continue
            except (EOFError, KeyboardInterrupt):
                print("\nExecução encerrada.")
                break

            try:
                match opcao:
                    case 1:
                        menu_crud(repositorio)
                    case 2:
                        menu_operacoes(repositorio)
                    case 3:
                        historico_trocas(repositorio)
                    case 4:
                        resumo_sistema(repositorio)
                    case 5:
                        menu_exportacao(repositorio)
                    case 6:
                        menu_clima(catalogo_clima)
                    case 0:
                        print("\nPrograma finalizado. Obrigado por utilizar a Zyra!")
                    case _:
                        print("\nOpção inválida.")
            except ValueError as erro:
                print(f"\nOperação inválida: {erro}")
            except ErroBanco as erro:
                print(f"\nErro de banco: {erro}")
                if erro.__cause__ is not None:
                    print(f"Detalhes técnicos: {erro.__cause__}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
