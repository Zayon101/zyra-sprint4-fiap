"""Menus do Zyra, delegando operações às funções de cada módulo."""

from sistema.constantes import PONTOS_POR_PASSAGEM, VALOR_PASSAGEM
from sistema.exportacao import exportar_consulta
from sistema.operacoes import adicionar_pontos, mostrar_passagens, trocar_pontos_por_passagem
from sistema.usuarios import alterar_usuario, cadastrar_usuario, consultar_usuario, excluir_usuario, listar_usuarios
from sistema.utils import formatar_reais, pausar, validar_numero


def menu_crud(repositorio):
    """Exibe opções de CREATE, READ, UPDATE e DELETE no Oracle."""
    opcao = -1
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
                cadastrar_usuario(repositorio)
            case 2:
                listar_usuarios(repositorio)
            case 3:
                consultar_usuario(repositorio)
            case 4:
                alterar_usuario(repositorio)
            case 5:
                excluir_usuario(repositorio)
            case 0:
                print("\nVoltando ao menu principal...")
            case _:
                print("\nOpção inválida.")


def menu_operacoes(repositorio):
    """Exibe operações de saldo e passagens persistidas no Oracle."""
    opcao = -1
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
                adicionar_pontos(repositorio)
            case 2:
                mostrar_passagens()
                pausar()
            case 3:
                trocar_pontos_por_passagem(repositorio)
            case 0:
                print("\nVoltando ao menu principal...")
            case _:
                print("\nOpção inválida.")


def menu_exportacao(repositorio):
    """Permite exportar consultas SQL sem modificar os dados do Oracle."""
    opcao = -1
    tipos = {1: "usuarios", 2: "usuario", 3: "historico", 4: "resumo"}
    while opcao != 0:
        print("\n" + "=" * 40)
        print("           EXPORTAR CONSULTAS JSON")
        print("=" * 40)
        print("[1] Todos os usuários")
        print("[2] Usuário por ID")
        print("[3] Histórico de trocas por usuário")
        print("[4] Resumo geral do sistema")
        print("-" * 40)
        print("[0] Voltar")
        opcao = validar_numero("Escolha uma opção: ")
        if opcao == 0:
            print("\nVoltando ao menu principal...")
            continue
        if opcao not in tipos:
            print("\nOpção inválida.")
            continue

        id_usuario = None
        if opcao in (2, 3):
            id_usuario = validar_numero("Digite o ID do usuário: ")
            if id_usuario <= 0:
                print("\nErro: informe um ID maior que zero.")
                pausar()
                continue

        try:
            caminho = exportar_consulta(repositorio, tipos[opcao], id_usuario)
        except (OSError, TypeError, ValueError) as erro:
            print(f"\nErro ao criar arquivo JSON: {erro}")
        else:
            if caminho is None:
                print("\nUsuário não encontrado. Nenhum arquivo foi criado.")
            else:
                print("\nConsulta exportada com sucesso!")
                print(f"Arquivo: {caminho}")
                print("Aviso: o JSON pode conter dados de usuários; compartilhe com cuidado.")
        pausar()


def exibir_boas_vindas():
    """Exibe a tela de boas-vindas sem operações de persistência."""
    print("\n" + "=" * 40)
    print("        Bem-vindo ao ZYRA")
    print("     Converta pontos SoulUp em")
    print("        passagens de metrô")
    print("=" * 40)
    print(f"\n1 passagem = {PONTOS_POR_PASSAGEM} pontos")
    print(f"Valor da passagem: {formatar_reais(VALOR_PASSAGEM)}")
    pausar()


def exibir_menu():
    """Mostra opções do sistema."""
    print("\n" + "=" * 40)
    print("                 ZYRA")
    print("=" * 40)
    print("[1] Gerenciar usuários")
    print("[2] Pontos e passagens")
    print("[3] Histórico de trocas")
    print("[4] Resumo do sistema")
    print("[5] Exportar consultas em JSON")
    print("[6] Condições para sua viagem (clima)")
    print("[7] Conectar SQL / preparar tabelas")
    print("[8] Abrir página web")
    print("-" * 40)
    print("[0] Encerrar")
    print("=" * 40)
