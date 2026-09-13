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
Usamos " para documentação de funções e # para comentários de linha ou bloco
'''


# ============================
# Imports para gerenciar JSON
# ============================

import json
from pathlib import Path



# =========================
# CONSTANTES
# =========================

# Obtém a pasta onde o próprio arquivo Python está salvo
PASTA_PROGRAMA = Path(__file__).resolve().parent

# Define que o JSON será criado na mesma pasta do programa
ARQUIVO_DADOS = PASTA_PROGRAMA / "dados_zyra.json"

# Valores fixos utilizados para definir o sistema de pontos e passagens
BONUS_CADASTRO = 500
VALOR_PASSAGEM = 5.40
PONTOS_POR_PASSAGEM = 587
# Calcula automaticamente quanto cada ponto representa em reais
VALOR_POR_PONTO = VALOR_PASSAGEM / PONTOS_POR_PASSAGEM

# Tupla com as opções fixas de passagem:
# (nome, quantidade de viagens, custo em pontos)
TIPOS_PASSAGEM = (
    ("Unitária", 1, PONTOS_POR_PASSAGEM),
    ("Ida e volta", 2, PONTOS_POR_PASSAGEM * 2),
    ("Pacote com 5 viagens", 5, PONTOS_POR_PASSAGEM * 5)
)



# =========================
# FUNÇÕES DE APOIO
# =========================

def formatar_reais(valor):
    """Recebe um valor numérico e retorna o valor formatado em reais."""
    return f"R$ {valor:.2f}".replace(".", ",")


def validar_nome(mensagem="Digite o nome do usuário: "):
    """Solicita e retorna um nome válido."""
    # Repete a entrada até que um nome válido seja informado
    while True:
        nome = input(mensagem).strip()

        # Remove os espaços apenas para verificar se o restante possui somente letras
        if len(nome) >= 3 and nome.replace(" ", "").isalpha():
            return nome

        print("Erro: digite um nome válido com pelo menos 3 letras.")


def validar_numero(mensagem):
    """Solicita e retorna um número inteiro validado."""
    numero_texto = input(mensagem).strip()

    # Valida o texto antes da conversão para evitar ValueError nos submenus
    while numero_texto.isdigit() == False:
        print("Erro: digite apenas números.")
        numero_texto = input(mensagem).strip()

    return int(numero_texto)


def pausar():
    """Pausa a execução até o usuário pressionar ENTER."""
    input("\nPressione ENTER para continuar...")


def gerar_id(lista_usuarios):
    """Recebe a lista de usuários e retorna o próximo ID disponível."""
    maior_id = 0

    # Percorre os usuários para localizar o maior ID já utilizado
    for usuario in lista_usuarios:
        if usuario["id"] > maior_id:
            maior_id = usuario["id"]

    # O próximo cadastro recebe um número acima do maior ID encontrado
    return maior_id + 1


def buscar_indice_por_id(lista_usuarios, id_usuario):
    """Recebe a lista e um ID e retorna o índice encontrado ou None."""
    # Procura o ID e retorna a posição correspondente dentro da lista
    for i in range(len(lista_usuarios)):
        if lista_usuarios[i]["id"] == id_usuario:
            return i

    return None



# =========================
# GERENCIAR ARQUIVO
# =========================

def salvar_dados(lista_usuarios):
    """Recebe a lista de usuários e salva os dados no arquivo JSON."""
    arquivo = None
    sucesso = False

    try:
        # Abre o arquivo JSON em modo de escrita e salva a lista em formato de texto
        # Caso o arquivo não exista, ele será criado automaticamente
        arquivo = open(ARQUIVO_DADOS, "w", encoding="utf-8")
        json.dump(lista_usuarios, arquivo, ensure_ascii=False, indent=4)

    except (OSError, TypeError) as erro:
        print(f"\nErro ao salvar os dados: {erro}")

    else:
        sucesso = True

    finally:
        # Garante que o arquivo seja fechado mesmo se ocorrer algum erro
        if arquivo is not None:
            arquivo.close()

    return sucesso


def carregar_dados():
    """Carrega os dados do arquivo JSON e retorna a lista de usuários."""
    arquivo = None
    lista_usuarios = []

    try:
        # Abre o arquivo salvo anteriormente e converte o JSON para dados do Python
        arquivo = open(ARQUIVO_DADOS, "r", encoding="utf-8")
        lista_usuarios = json.load(arquivo)

        # Verifica se o conteúdo principal do JSON é uma lista
        if isinstance(lista_usuarios, list) == False:
            print("\nErro: o arquivo de dados possui um formato inválido.")
            lista_usuarios = []

        else:
            # Verifica se cada usuário da lista está armazenado como dicionário
            for usuario in lista_usuarios:
                if isinstance(usuario, dict) == False:
                    print("\nErro: o arquivo de dados possui um formato inválido.")
                    lista_usuarios = []
                    break

    except FileNotFoundError:
        # Na primeira execução o arquivo ainda pode não existir
        lista_usuarios = []

    except (OSError, json.JSONDecodeError) as erro:
        # Trata problemas de leitura ou um JSON com sintaxe inválida
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
    """Recebe um ID e retorna um novo usuário em formato de dicionário."""
    print("\n" + "=" * 40)
    print("           CADASTRO DE USUÁRIO")
    print("=" * 40)

    nome = validar_nome()

    # Cada usuário é representado por um dicionário
    return {
        "id": id_usuario,
        "nome": nome,
        "pontos": BONUS_CADASTRO,
        "historico": []
    }


def inserir_usuario(lista_usuarios, novo_usuario):
    """Recebe a lista e um usuário, insere o cadastro e retorna o resultado."""
    sucesso = False

    try:
        # Adiciona o novo dicionário à lista principal de usuários
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
    """Recebe a lista de usuários e exibe os cadastros existentes."""
    print("\n" + "=" * 40)
    print("           USUÁRIOS CADASTRADOS")
    print("=" * 40)

    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")

    else:
        # Percorre todos os usuários para exibir seus dados e saldo equivalente
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
    """Recebe a lista de usuários e permite consultar um cadastro por ID."""
    print("\n" + "=" * 40)
    print("           CONSULTAR USUÁRIO")
    print("=" * 40)

    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        pausar()
        return

    listar_usuarios(lista_usuarios, False)

    # O ID é utilizado para localizar o usuário sem depender da posição exibida
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
    """Recebe a lista de usuários e altera nome ou pontos de um cadastro."""
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

        # Cria uma nova versão mantendo os dados que não foram alterados
        usuario_atualizado = {
            "id": usuario["id"],
            "nome": novo_nome,
            "pontos": usuario["pontos"],
            # Faz uma cópia do histórico para preservar as trocas anteriores
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
        # Substitui somente o cadastro escolhido pela versão atualizada
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
    """Recebe a lista de usuários e remove um cadastro pelo ID."""
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
        # Remove da lista o usuário localizado pelo ID
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
    """Recebe a lista de usuários e retorna o índice do usuário escolhido."""
    if len(lista_usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        return None

    # Se houver apenas um cadastro, não é necessário pedir o ID
    if len(lista_usuarios) == 1:
        print("\nUsuário selecionado automaticamente:")
        print(f"ID {lista_usuarios[0]['id']} - {lista_usuarios[0]['nome']}")
        return 0

    listar_usuarios(lista_usuarios, False)

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    indice = buscar_indice_por_id(lista_usuarios, id_usuario)

    # Continua solicitando até que seja informado um ID existente
    while indice is None:
        print("Erro: usuário inválido.")
        id_usuario = validar_numero("Digite o ID do usuário: ")
        indice = buscar_indice_por_id(lista_usuarios, id_usuario)

    return indice


def adicionar_pontos(usuario):
    """Recebe um usuário e retorna seus dados com o saldo atualizado."""
    print("\n" + "=" * 40)
    print("           ADICIONAR PONTOS")
    print("=" * 40)

    pontos = 0

    while pontos <= 0:
        pontos = validar_numero("\nDigite a quantidade de pontos: ")

        if pontos <= 0:
            print("Informe um valor maior que zero.")

    # Calcula o novo saldo sem alterar os outros dados do usuário
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
    """Exibe as opções de passagens disponíveis no sistema."""
    print("\n" + "=" * 40)
    print("           PASSAGENS DISPONÍVEIS")
    print("=" * 40)

    # Percorre a tupla de opções para montar o menu de passagens
    for i in range(len(TIPOS_PASSAGEM)):
        passagem = TIPOS_PASSAGEM[i]

        print(
            f"[{i + 1}] {passagem[0]} | "
            f"{passagem[1]} viagem(ns) | "
            f"{passagem[2]} pontos | "
            f"{formatar_reais(passagem[1] * VALOR_PASSAGEM)}"
        )


def trocar_pontos_por_passagem(usuario):
    """Recebe um usuário e retorna seus dados após a tentativa de troca."""
    print("\n" + "=" * 40)
    print("           TROCA DE PONTOS")
    print("=" * 40)

    mostrar_passagens()

    opcao = 0

    while opcao < 1 or opcao > len(TIPOS_PASSAGEM):
        opcao = validar_numero("\nEscolha a passagem desejada: ")

        if opcao < 1 or opcao > len(TIPOS_PASSAGEM):
            print("Erro: opção inválida.")

    # Como a lista visual começa em 1, subtrai 1 para acessar o índice da tupla
    passagem = TIPOS_PASSAGEM[opcao - 1]

    nome_passagem = passagem[0]
    quantidade_viagens = passagem[1]
    custo = passagem[2]
    valor_reais = quantidade_viagens * VALOR_PASSAGEM

    novo_saldo = usuario["pontos"]

    # Cria uma cópia do histórico antes de registrar uma nova troca
    novo_historico = usuario["historico"][:]

    # A troca só é realizada quando o usuário possui pontos suficientes
    if usuario["pontos"] >= custo:
        novo_saldo -= custo

        # Registra os dados da operação em um novo dicionário
        nova_troca = {
            "passagem": nome_passagem,
            "custo": custo,
            "viagens": quantidade_viagens,
            "valor": valor_reais
        }

        # Adiciona a troca ao histórico que será retornado com o usuário
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
    """Recebe um usuário e exibe seu histórico de trocas."""
    print("\n" + "=" * 40)
    print("           HISTÓRICO DE TROCAS")
    print("=" * 40)

    if len(usuario["historico"]) == 0:
        print("\nNenhuma troca realizada.")

    else:
        print(f"\nHistórico de {usuario['nome']}:")

        # Percorre todas as trocas armazenadas no histórico do usuário
        for troca in usuario["historico"]:
            print(
                f"[✓] {troca['passagem']} | "
                f"{troca['viagens']} viagem(ns) | "
                f"{troca['custo']} pontos | "
                f"{formatar_reais(troca['valor'])}"
            )

    pausar()


def resumo_sistema(lista_usuarios):
    """Recebe a lista de usuários e exibe as informações gerais do sistema."""
    print("\n" + "=" * 40)
    print("           RESUMO DO SISTEMA")
    print("=" * 40)

    # Variáveis acumuladoras usadas para calcular os totais do sistema
    total_pontos = 0
    total_operacoes = 0
    total_viagens = 0
    valor_resgatado = 0

    # Percorre todos os usuários e soma seus dados
    for usuario in lista_usuarios:
        total_pontos += usuario["pontos"]
        total_operacoes += len(usuario["historico"])

        # Percorre também o histórico de cada usuário para somar as viagens
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
                    # A função retorna o usuário atualizado e o main da operação
                    # substitui somente a posição correspondente na lista
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



# =========================
# PROGRAMA PRINCIPAL
# =========================

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



# Iniciar o programa
main()
