"""Validações, formatação e auxiliares reutilizados pelos demais módulos."""

from datetime import datetime

from sistema.regras import validar_nome_usuario


def formatar_reais(valor: float) -> str:
    """Recebe um valor numérico e retorna o valor formatado em reais."""
    return f"R$ {valor:.2f}".replace(".", ",")


def validar_nome(mensagem: str = "Digite o nome do usuário: ") -> str:
    """Solicita o nome e usa exatamente a validação de negócio da API."""
    while True:
        nome = input(mensagem)
        try:
            return validar_nome_usuario(nome)
        except ValueError as erro:
            print(f"Erro: {erro}")


def validar_numero(mensagem: str) -> int:
    """Solicita e retorna um número inteiro validado."""
    numero_texto = input(mensagem).strip()

    # Valida o texto antes da conversão para evitar ValueError nos submenus
    while not numero_texto.isdigit():
        print("Erro: digite apenas números.")
        numero_texto = input(mensagem).strip()

    return int(numero_texto)


def pausar() -> None:
    """Pausa a execução até o usuário pressionar ENTER."""
    input("\nPressione ENTER para continuar...")



def formatar_data_troca(data: datetime | str) -> str:
    """Formata uma data retornada pelo Oracle (ou texto ISO nos testes)."""
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(data, str):
        try:
            return datetime.fromisoformat(data).strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            pass
    return "Data indisponível"
