'''
Integrantes:
Carolina Kotz Rodrigues - RM 571876 - 1TDSPH
Felipe Motitsuki Tan - RM 570770 - 1TDSPH
Gabriel Feitosa de Lima - RM 573026 - 1TDSPH
João Gabriel Dantas Moura - RM 573101 - 1TDSPH
Záyon Alves Marques - RM 571205 - 1TDSPH

============================================================
Zyra - Sprint 3
Challenge FIAP 2026
============================================================
'''



# ============================
# Imports para gerenciar JSON
# ============================

import json
from pathlib import Path



# =========================
# CONSTANTES
# =========================

PASTA_PROGRAMA = Path(__file__).resolve().parent
ARQUIVO_DADOS = PASTA_PROGRAMA / "dados_zyra.json"

BONUS_CADASTRO = 500
VALOR_PASSAGEM = 5.40
PONTOS_POR_PASSAGEM = 587
VALOR_POR_PONTO = VALOR_PASSAGEM / PONTOS_POR_PASSAGEM

TIPOS_PASSAGEM = (
    ("Unitária", 1, PONTOS_POR_PASSAGEM),
    ("Ida e volta", 2, PONTOS_POR_PASSAGEM * 2),
    ("Pacote com 5 viagens", 5, PONTOS_POR_PASSAGEM * 5)
)



# =========================
# FUNÇÕES DE APOIO
# =========================

def formatar_reais(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def validar_nome(mensagem="Digite o nome do usuário: "):
    while True:
        nome = input(mensagem).strip()

        if len(nome) >= 3 and nome.replace(" ", "").isalpha():
            return nome

        print("Erro: digite um nome válido com pelo menos 3 letras.")


def validar_numero(mensagem):
    numero_texto = input(mensagem).strip()

    while numero_texto.isdigit() == False:
        print("Erro: digite apenas números.")
        numero_texto = input(mensagem).strip()

    return int(numero_texto)


def pausar():
    input("\nPressione ENTER para continuar...")


def gerar_id(lista_usuarios):
    maior_id = 0

    for usuario in lista_usuarios:
        if usuario["id"] > maior_id:
            maior_id = usuario["id"]

    return maior_id + 1


def buscar_indice_por_id(lista_usuarios, id_usuario):
    for i in range(len(lista_usuarios)):
        if lista_usuarios[i]["id"] == id_usuario:
            return i

    return None



# =========================
# GERENCIAR ARQUIVO
# =========================

def salvar_dados(lista_usuarios):
    arquivo = None
    sucesso = False

    try:
        arquivo = open(ARQUIVO_DADOS, "w", encoding="utf-8")
        json.dump(lista_usuarios, arquivo, ensure_ascii=False, indent=4)

    except (OSError, TypeError) as erro:
        print(f"\nErro ao salvar os dados: {erro}")

    else:
        sucesso = True

    finally:
        if arquivo is not None:
            arquivo.close()

    return sucesso


def carregar_dados():
    arquivo = None
    lista_usuarios = []

    try:
        arquivo = open(ARQUIVO_DADOS, "r", encoding="utf-8")
        lista_usuarios = json.load(arquivo)

    except FileNotFoundError:
        lista_usuarios = []

    except (OSError, json.JSONDecodeError) as erro:
        print(f"\nErro ao carregar os dados: {erro}")
        lista_usuarios = []

    else:
        print("Dados carregados com sucesso.")

    finally:
        if arquivo is not None:
            arquivo.close()

    return lista_usuarios



# =========================
# CRUD DE USUÁRIOS
# =========================

def criar_usuario(id_usuario):
    print("\n" + "=" * 40)
    print("           CADASTRO DE USUÁRIO")
    print("=" * 40)

    nome = validar_nome()

    return {
        "id": id_usuario,
        "nome": nome,
        "pontos": BONUS_CADASTRO,
        "historico": []
    }


def inserir_usuario(lista_usuarios, novo_usuario):
    sucesso = False

    try:
        lista_usuarios.append(novo_usuario)

    except (AttributeError, TypeError) as erro:
        print(f"\nErro ao cadastrar usuário: {erro}")

    else:
        sucesso = True
        print("\nUsuário cadastrado com sucesso!")
        print(f"ID: {novo_usuario['id']}")
        print(f"Bônus inicial: {novo_usuario['pontos']} pontos")

    finally:
        print("Operação de cadastro finalizada.")

    return sucesso


def listar_usuarios(lista_usuarios, pausar_ao_final=True):
    print("\n" + "=" * 40)
    print("           USUÁRIOS CADASTRADOS")
    print("=" * 40)

    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")

    else:
        for usuario in lista_usuarios:
            saldo_reais = usuario["pontos"] * VALOR_POR_PONTO

            print(
                f"ID {usuario['id']} | "
                f"{usuario['nome']} | "
                f"{usuario['pontos']} pontos | "
                f"{formatar_reais(saldo_reais)}"
            )

    if pausar_ao_final:
        pausar()


def consultar_usuario(lista_usuarios):
    print("\n" + "=" * 40)
    print("           CONSULTAR USUÁRIO")
    print("=" * 40)

    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        pausar()
        return

    listar_usuarios(lista_usuarios, False)

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    indice = buscar_indice_por_id(lista_usuarios, id_usuario)

    if indice is None:
        print("Erro: usuário não encontrado.")

    else:
        usuario = lista_usuarios[indice]

        print("\nUsuário encontrado:")
        print(f"ID: {usuario['id']}")
        print(f"Nome: {usuario['nome']}")
        print(f"Pontos: {usuario['pontos']}")
        print(f"Trocas realizadas: {len(usuario['historico'])}")

    pausar()


def alterar_usuario(lista_usuarios):
    print("\n" + "=" * 40)
    print("            ALTERAR USUÁRIO")
    print("=" * 40)

    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        pausar()
        return False

    listar_usuarios(lista_usuarios, False)

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    indice = buscar_indice_por_id(lista_usuarios, id_usuario)

    if indice is None:
        print("Erro: usuário não encontrado.")
        pausar()
        return False

    usuario = lista_usuarios[indice]

    print("\n[1] Alterar nome")
    print("[2] Alterar pontos")
    print("[0] Cancelar")

    opcao = validar_numero("Escolha uma opção: ")

    if opcao == 0:
        print("Alteração cancelada.")
        pausar()
        return False

    if opcao == 1:
        novo_nome = validar_nome("Digite o novo nome: ")
        usuario_atualizado = {
            "id": usuario["id"],
            "nome": novo_nome,
            "pontos": usuario["pontos"],
            "historico": usuario["historico"][:]
        }

    elif opcao == 2:
        novos_pontos = validar_numero("Digite o novo saldo em pontos: ")
        usuario_atualizado = {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "pontos": novos_pontos,
            "historico": usuario["historico"][:]
        }

    else:
        print("Erro: opção inválida.")
        pausar()
        return False

    sucesso = False

    try:
        lista_usuarios[indice] = usuario_atualizado

    except (IndexError, KeyError, TypeError) as erro:
        print(f"\nErro ao alterar usuário: {erro}")

    else:
        sucesso = True
        print("\nUsuário alterado com sucesso!")

    finally:
        print("Operação de alteração finalizada.")

    pausar()
    return sucesso


def excluir_usuario(lista_usuarios):
    print("\n" + "=" * 40)
    print("            EXCLUIR USUÁRIO")
    print("=" * 40)

    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        pausar()
        return False

    listar_usuarios(lista_usuarios, False)

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    indice = buscar_indice_por_id(lista_usuarios, id_usuario)

    if indice is None:
        print("Erro: usuário não encontrado.")
        pausar()
        return False

    usuario = lista_usuarios[indice]

    print(f"\nExcluir o usuário {usuario['nome']}?")
    print("[1] Sim")
    print("[2] Não")

    confirmacao = validar_numero("Escolha uma opção: ")

    if confirmacao != 1:
        print("Exclusão cancelada.")
        pausar()
        return False

    sucesso = False

    try:
        lista_usuarios.pop(indice)

    except (IndexError, TypeError) as erro:
        print(f"\nErro ao excluir usuário: {erro}")

    else:
        sucesso = True
        print("\nUsuário excluído com sucesso!")

    finally:
        print("Operação de exclusão finalizada.")

    pausar()
    return sucesso



# =========================
# OPERAÇÕES ZYRA
# =========================

def escolher_usuario(lista_usuarios):
    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        return None

    if len(lista_usuarios) == 1:
        print("\nUsuário selecionado automaticamente:")
        print(f"ID {lista_usuarios[0]['id']} - {lista_usuarios[0]['nome']}")
        return 0

    listar_usuarios(lista_usuarios, False)

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    indice = buscar_indice_por_id(lista_usuarios, id_usuario)

    while indice is None:
        print("Erro: usuário inválido.")
        id_usuario = validar_numero("Digite o ID do usuário: ")
        indice = buscar_indice_por_id(lista_usuarios, id_usuario)

    return indice


def adicionar_pontos(usuario):
    print("\n" + "=" * 40)
    print("           ADICIONAR PONTOS")
    print("=" * 40)

    pontos = 0

    while pontos <= 0:
        pontos = validar_numero("\nDigite a quantidade de pontos: ")

        if pontos <= 0:
            print("Informe um valor maior que zero.")

    novo_saldo = usuario["pontos"] + pontos

    usuario_atualizado = {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "pontos": novo_saldo,
        "historico": usuario["historico"][:]
    }

    print("\nPontos adicionados com sucesso!")
    print(f"Novo saldo: {novo_saldo} pontos")
    print(
        f"Saldo em reais: "
        f"{formatar_reais(novo_saldo * VALOR_POR_PONTO)}"
    )

    pausar()
    return usuario_atualizado


def mostrar_passagens():
    print("\n" + "=" * 40)
    print("           PASSAGENS DISPONÍVEIS")
    print("=" * 40)

    for i in range(len(TIPOS_PASSAGEM)):
        passagem = TIPOS_PASSAGEM[i]

        print(
            f"[{i + 1}] {passagem[0]} | "
            f"{passagem[1]} viagem(ns) | "
            f"{passagem[2]} pontos | "
            f"{formatar_reais(passagem[1] * VALOR_PASSAGEM)}"
        )


def trocar_pontos_por_passagem(usuario):
    print("\n" + "=" * 40)
    print("           TROCA DE PONTOS")
    print("=" * 40)

    mostrar_passagens()

    opcao = 0

    while opcao < 1 or opcao > len(TIPOS_PASSAGEM):
        opcao = validar_numero("\nEscolha a passagem desejada: ")

        if opcao < 1 or opcao > len(TIPOS_PASSAGEM):
            print("Erro: opção inválida.")

    passagem = TIPOS_PASSAGEM[opcao - 1]

    nome_passagem = passagem[0]
    quantidade_viagens = passagem[1]
    custo = passagem[2]
    valor_reais = quantidade_viagens * VALOR_PASSAGEM

    novo_saldo = usuario["pontos"]
    novo_historico = usuario["historico"][:]

    if usuario["pontos"] >= custo:
        novo_saldo -= custo

        nova_troca = {
            "passagem": nome_passagem,
            "custo": custo,
            "viagens": quantidade_viagens,
            "valor": valor_reais
        }

        novo_historico.append(nova_troca)

        print("\nTroca realizada com sucesso!")
        print(f"Passagem adquirida: {nome_passagem}")
        print(f"Saldo atual: {novo_saldo} pontos")

    else:
        print("\nSaldo insuficiente.")
        print(f"Saldo atual: {usuario['pontos']} pontos")
        print(f"Faltam: {custo - usuario['pontos']} pontos")

    pausar()

    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "pontos": novo_saldo,
        "historico": novo_historico
    }


def historico_trocas(usuario):
    print("\n" + "=" * 40)
    print("           HISTÓRICO DE TROCAS")
    print("=" * 40)

    if len(usuario["historico"]) == 0:
        print("\nNenhuma troca realizada.")

    else:
        print(f"\nHistórico de {usuario['nome']}:")

        for troca in usuario["historico"]:
            print(
                f"[✓] {troca['passagem']} | "
                f"{troca['viagens']} viagem(ns) | "
                f"{troca['custo']} pontos | "
                f"{formatar_reais(troca['valor'])}"
            )

    pausar()


def resumo_sistema(lista_usuarios):
    print("\n" + "=" * 40)
    print("           RESUMO DO SISTEMA")
    print("=" * 40)

    total_pontos = 0
    total_operacoes = 0
    total_viagens = 0
    valor_resgatado = 0

    for usuario in lista_usuarios:
        total_pontos += usuario["pontos"]
        total_operacoes += len(usuario["historico"])

        for troca in usuario["historico"]:
            total_viagens += troca["viagens"]
            valor_resgatado += troca["valor"]

    print(f"Total de usuários: {len(lista_usuarios)}")
    print(f"Total de pontos: {total_pontos}")
    print(
        f"Valor total em saldo: "
        f"{formatar_reais(total_pontos * VALOR_POR_PONTO)}"
    )
    print(f"Total de trocas: {total_operacoes}")
    print(f"Total de viagens resgatadas: {total_viagens}")
    print(f"Valor total resgatado: {formatar_reais(valor_resgatado)}")

    pausar()



# =========================
# SUBMENUS
# =========================

def menu_crud(lista_usuarios):
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
                novo_id = gerar_id(lista_usuarios)
                novo_usuario = criar_usuario(novo_id)

                if inserir_usuario(lista_usuarios, novo_usuario):
                    salvar_dados(lista_usuarios)

                pausar()

            case 2:
                listar_usuarios(lista_usuarios)

            case 3:
                consultar_usuario(lista_usuarios)

            case 4:
                if alterar_usuario(lista_usuarios):
                    salvar_dados(lista_usuarios)

            case 5:
                if excluir_usuario(lista_usuarios):
                    salvar_dados(lista_usuarios)

            case 0:
                print("\nVoltando ao menu principal...")

            case _:
                print("\nOpção inválida.")


def menu_operacoes(lista_usuarios):
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
                indice = escolher_usuario(lista_usuarios)

                if indice is not None:
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



# =========================
# PROGRAMA PRINCIPAL
# =========================

def exibir_boas_vindas():
    print("\n" + "=" * 40)
    print("        Bem-vindo ao ZYRA")
    print("     Converta pontos SoulUp em")
    print("        passagens de metrô")
    print("=" * 40)
    print(f"\n1 passagem = {PONTOS_POR_PASSAGEM} pontos")
    print(f"Valor da passagem: {formatar_reais(VALOR_PASSAGEM)}")

    pausar()


def exibir_menu():
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


def main():
    lista_usuarios = carregar_dados()
    opcao = -1

    exibir_boas_vindas()

    while opcao != 0:
        exibir_menu()

        try:
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
                    salvar_dados(lista_usuarios)
                    print(
                        "\nPrograma finalizado. "
                        "Obrigado por utilizar a Zyra!"
                    )

                case _:
                    print("\nOpção inválida.")



# Iniciar o programa
main()
