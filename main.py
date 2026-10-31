"""Ponto de entrada do Zyra - Sprint 4 (Etapa 2: conexão Oracle)."""

from menus import exibir_boas_vindas, exibir_menu, menu_crud, menu_operacoes
from operacoes import escolher_usuario, historico_trocas, resumo_sistema
from persistencia import carregar_dados, salvar_dados
from utils import pausar


def main():
    """Carrega os dados e controla o fluxo principal do programa."""
    # Recupera os dados salvos antes de iniciar a navegação
    lista_usuarios = carregar_dados()
    opcao = -1

    exibir_boas_vindas()

    # O programa permanece em execução até que seja escolhida a opção 0
    while opcao != 0:
        exibir_menu()

        try:
            # No menu principal o try/except é utilizado para capturar entradas inválidas
            opcao = int(input("Escolha uma opção: "))

        except ValueError:
            print("\nErro: digite apenas números.")
            opcao = -1

        else:
            match opcao:
                case 1:
                    menu_crud(lista_usuarios)

                case 2:
                    menu_operacoes(lista_usuarios)

                case 3:
                    indice = escolher_usuario(lista_usuarios)

                    if indice is not None:
                        historico_trocas(lista_usuarios[indice])
                    else:
                        pausar()

                case 4:
                    resumo_sistema(lista_usuarios)

                case 0:
                    # Faz um último salvamento antes de encerrar o programa
                    salvar_dados(lista_usuarios)
                    print(
                        "\nPrograma finalizado. "
                        "Obrigado por utilizar a Zyra!"
                    )

                case _:
                    print("\nOpção inválida.")


if __name__ == "__main__":
    main()
