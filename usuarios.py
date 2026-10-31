"""CRUD de usuários da Sprint 3, preservado para posterior migração ao SQL."""

from constantes import BONUS_CADASTRO, VALOR_POR_PONTO
from utils import (
    buscar_indice_por_id,
    formatar_reais,
    pausar,
    validar_nome,
    validar_numero,
)


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
