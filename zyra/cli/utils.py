"""Validações, formatação e auxiliares reutilizados pelos demais módulos."""

from zyra.core.constantes import MAX_CARACTERES_NOME


def formatar_reais(valor):
    """Recebe um valor numérico e retorna o valor formatado em reais."""
    return f"R$ {valor:.2f}".replace(".", ",")


def validar_nome(mensagem="Digite o nome do usuário: "):
    """Solicita e retorna um nome válido."""
    # Repete a entrada até que um nome válido seja informado
    while True:
        nome = input(mensagem).strip()

        # Remove os espaços apenas para verificar se o restante possui somente letras
        if 3 <= len(nome) <= MAX_CARACTERES_NOME and nome.replace(" ", "").isalpha():
            return nome

        print(f"Erro: informe de 3 a {MAX_CARACTERES_NOME} letras (espaços permitidos).")


def validar_numero(mensagem):
    """Solicita e retorna um número inteiro validado."""
    numero_texto = input(mensagem).strip()

    # Valida o texto antes da conversão para evitar ValueError nos submenus
    while not numero_texto.isdigit():
        print("Erro: digite apenas números.")
        numero_texto = input(mensagem).strip()

    return int(numero_texto)


def pausar():
    """Pausa a execução até o usuário pressionar ENTER."""
    input("\nPressione ENTER para continuar...")



def formatar_data_troca(data):
    """Formata uma data retornada pelo Oracle (ou texto ISO nos testes)."""
    from datetime import datetime

    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(data, str):
        try:
            return datetime.fromisoformat(data).strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            pass
    return "Data indisponível"
