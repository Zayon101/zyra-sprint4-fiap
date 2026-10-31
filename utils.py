"""Validações, formatação e auxiliares reutilizados pelos demais módulos."""


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
