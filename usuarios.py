"""Interações do CRUD de usuários; acesso SQL isolado em repositorio.py."""

from constantes import BONUS_CADASTRO, VALOR_POR_PONTO
from utils import formatar_reais, pausar, validar_nome, validar_numero


def listar_usuarios(repositorio, pausar_ao_final=True):
    """Exibe os cadastros consultados no Oracle e devolve os resultados."""
    usuarios = repositorio.listar_usuarios()
    print("\n" + "=" * 40)
    print("           USUÁRIOS CADASTRADOS")
    print("=" * 40)
    if not usuarios:
        print("Nenhum usuário cadastrado.")
    else:
        for usuario in usuarios:
            reais = usuario["pontos"] * VALOR_POR_PONTO
            print(
                f"ID {usuario['id']} | {usuario['nome']} | "
                f"{usuario['pontos']} pontos | {formatar_reais(reais)}"
            )
    if pausar_ao_final:
        pausar()
    return usuarios


def cadastrar_usuario(repositorio):
    """Solicita um nome e faz INSERT no banco por meio do repositório."""
    print("\n" + "=" * 40)
    print("           CADASTRO DE USUÁRIO")
    print("=" * 40)
    nome = validar_nome()
    id_usuario = repositorio.criar_usuario(nome)
    print(f"\nUsuário cadastrado com sucesso! ID: {id_usuario}")
    print(f"Bônus inicial: {BONUS_CADASTRO} pontos")
    pausar()


def consultar_usuario(repositorio):
    """Consulta o usuário por ID usando SELECT parametrizado."""
    print("\n" + "=" * 40)
    print("           CONSULTAR USUÁRIO")
    print("=" * 40)
    if not listar_usuarios(repositorio, False):
        pausar()
        return

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    usuario = repositorio.consultar_usuario(id_usuario)
    if usuario is None:
        print("Erro: usuário não encontrado.")
    else:
        print("\nUsuário encontrado:")
        print(f"ID: {usuario['id']}")
        print(f"Nome: {usuario['nome']}")
        print(f"Pontos: {usuario['pontos']}")
        print(f"Trocas realizadas: {len(usuario['historico'])}")
    pausar()


def alterar_usuario(repositorio):
    """Atualiza nome ou pontos de um cadastro identificado por ID."""
    print("\n" + "=" * 40)
    print("            ALTERAR USUÁRIO")
    print("=" * 40)
    if not listar_usuarios(repositorio, False):
        pausar()
        return

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    if repositorio.consultar_usuario(id_usuario) is None:
        print("Erro: usuário não encontrado.")
        pausar()
        return

    print("\n[1] Alterar nome")
    print("[2] Alterar pontos")
    print("[0] Cancelar")
    opcao = validar_numero("Escolha uma opção: ")
    if opcao == 1:
        sucesso = repositorio.alterar_nome(id_usuario, validar_nome("Digite o novo nome: "))
    elif opcao == 2:
        sucesso = repositorio.alterar_pontos(id_usuario, validar_numero("Digite o novo saldo em pontos: "))
    elif opcao == 0:
        print("Alteração cancelada.")
        pausar()
        return
    else:
        print("Erro: opção inválida.")
        pausar()
        return
    print("\nUsuário alterado com sucesso!" if sucesso else "Usuário não encontrado.")
    pausar()


def excluir_usuario(repositorio):
    """Exclui um cadastro do Oracle apenas após confirmação."""
    print("\n" + "=" * 40)
    print("            EXCLUIR USUÁRIO")
    print("=" * 40)
    if not listar_usuarios(repositorio, False):
        pausar()
        return

    id_usuario = validar_numero("\nDigite o ID do usuário: ")
    usuario = repositorio.consultar_usuario(id_usuario)
    if usuario is None:
        print("Erro: usuário não encontrado.")
        pausar()
        return
    print(f"\nExcluir o usuário {usuario['nome']}?")
    print("[1] Sim")
    print("[2] Não")
    if validar_numero("Escolha uma opção: ") != 1:
        print("Exclusão cancelada.")
    elif repositorio.excluir_usuario(id_usuario):
        print("\nUsuário excluído com sucesso!")
    else:
        print("Usuário não encontrado.")
    pausar()
