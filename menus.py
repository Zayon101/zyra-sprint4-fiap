"""Menus da aplicação e navegação entre funções."""

from constantes import PONTOS_POR_PASSAGEM, VALOR_PASSAGEM
from operacoes import adicionar_pontos, escolher_usuario, mostrar_passagens, trocar_pontos_por_passagem
from persistencia import salvar_dados
from usuarios import alterar_usuario, consultar_usuario, criar_usuario, excluir_usuario, inserir_usuario, listar_usuarios
from utils import formatar_reais, gerar_id, pausar, validar_numero


def menu_crud(lista_usuarios):
    """Recebe a lista de usuários e controla o submenu do CRUD."""
    opcao = -1

    # Mantém o submenu aberto até que o usuário escolha voltar
    while opcao != 0:
        print("\n" + "=" * 40)
        print("           GERENCIAR USUÁRIOS")
        print("=" * 40)
        print("[1] Cadastrar usuário")
        print("[2] Listar usuários")
        print("[3] Consultar por ID")
        print("[4] Alterar usuário")
        print("[5] Excluir usuário")
        print("-" * 40)
        print("[0] Voltar")

        opcao = validar_numero("Escolha uma opção: ")

        match opcao:
            case 1:
                # CREATE: gera o ID, cria o usuário e depois salva no arquivo
                novo_id = gerar_id(lista_usuarios)
                novo_usuario = criar_usuario(novo_id)

                if inserir_usuario(lista_usuarios, novo_usuario):
                    salvar_dados(lista_usuarios)

                pausar()

            case 2:
                # READ: exibe todos os usuários cadastrados
                listar_usuarios(lista_usuarios)

            case 3:
                # READ: consulta um cadastro específico pelo ID
                consultar_usuario(lista_usuarios)

            case 4:
                # UPDATE: salva o arquivo somente quando a alteração é concluída
                if alterar_usuario(lista_usuarios):
                    salvar_dados(lista_usuarios)

            case 5:
                # DELETE: remove o cadastro e atualiza o arquivo JSON
                if excluir_usuario(lista_usuarios):
                    salvar_dados(lista_usuarios)

            case 0:
                print("\nVoltando ao menu principal...")

            case _:
                print("\nOpção inválida.")


def menu_operacoes(lista_usuarios):
    """Recebe a lista de usuários e controla o submenu de pontos e passagens."""
    opcao = -1

    # Mantém as operações disponíveis até que seja escolhida a opção de voltar
    while opcao != 0:
        print("\n" + "=" * 40)
        print("          PONTOS E PASSAGENS")
        print("=" * 40)
        print("[1] Adicionar pontos")
        print("[2] Mostrar passagens")
        print("[3] Trocar pontos por passagem")
        print("-" * 40)
        print("[0] Voltar")

        opcao = validar_numero("Escolha uma opção: ")

        match opcao:
            case 1:
                indice = escolher_usuario(lista_usuarios)

                if indice is not None:
                    # A função retorna o usuário atualizado e substitui
                    # somente a posição correspondente na lista
                    lista_usuarios[indice] = adicionar_pontos(
                        lista_usuarios[indice]
                    )
                    salvar_dados(lista_usuarios)
                else:
                    pausar()

            case 2:
                mostrar_passagens()
                pausar()

            case 3:
                indice = escolher_usuario(lista_usuarios)

                if indice is not None:
                    # Atualiza o cadastro com o novo saldo e histórico de troca
                    lista_usuarios[indice] = trocar_pontos_por_passagem(
                        lista_usuarios[indice]
                    )
                    salvar_dados(lista_usuarios)
                else:
                    pausar()

            case 0:
                print("\nVoltando ao menu principal...")

            case _:
                print("\nOpção inválida.")


def exibir_boas_vindas():
    """Exibe a tela inicial do sistema."""
    print("\n" + "=" * 40)
    print("        Bem-vindo ao ZYRA")
    print("     Converta pontos SoulUp em")
    print("        passagens de metrô")
    print("=" * 40)
    print(f"\n1 passagem = {PONTOS_POR_PASSAGEM} pontos")
    print(f"Valor da passagem: {formatar_reais(VALOR_PASSAGEM)}")

    pausar()


def exibir_menu():
    """Exibe as opções do menu principal."""
    print("\n" + "=" * 40)
    print("                 ZYRA")
    print("=" * 40)
    print("[1] Gerenciar usuários")
    print("[2] Pontos e passagens")
    print("[3] Histórico de trocas")
    print("[4] Resumo do sistema")
    print("-" * 40)
    print("[0] Encerrar")
    print("=" * 40)
