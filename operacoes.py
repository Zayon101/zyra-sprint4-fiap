"""Regras de pontos, passagens, histórico e resumo do Zyra."""

from constantes import TIPOS_PASSAGEM, VALOR_PASSAGEM, VALOR_POR_PONTO
from usuarios import listar_usuarios
from utils import buscar_indice_por_id, formatar_reais, pausar, validar_numero


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
