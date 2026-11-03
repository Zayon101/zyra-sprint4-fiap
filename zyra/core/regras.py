"""Validações de negócio independentes do terminal e do Oracle."""

from zyra.core.constantes import MAX_CARACTERES_NOME, MAX_PONTOS, TIPOS_PASSAGEM


def validar_nome_usuario(nome: str) -> str:
    """Valida o nome para CLI, API e importação JSON.

    Aceita letras Unicode (inclusive acentos), espaços, hífens e apóstrofos,
    sem aceitar números ou caracteres de controle. Mantém a grafia digitada.
    """
    if not isinstance(nome, str):
        raise ValueError("O nome deve ser um texto.")
    nome = nome.strip()
    if (not 3 <= len(nome) <= MAX_CARACTERES_NOME
            or sum(letra.isalpha() for letra in nome) < 3
            or any(not (letra.isalpha() or letra in " -'’") for letra in nome)):
        raise ValueError(
            f"Informe um nome válido de 3 a {MAX_CARACTERES_NOME} caracteres "
            "(letras, espaços, hífens ou apóstrofos)."
        )
    return nome


def validar_saldo(pontos: int) -> int:
    """Valida um saldo inteiro dentro da capacidade da coluna NUMBER(12)."""
    if type(pontos) is not int or not 0 <= pontos <= MAX_PONTOS:
        raise ValueError(f"O saldo deve ser inteiro entre 0 e {MAX_PONTOS}.")
    return pontos


def validar_credito(quantidade: int) -> int:
    """Valida uma quantidade positiva de pontos para crédito."""
    if type(quantidade) is not int or not 1 <= quantidade <= MAX_PONTOS:
        raise ValueError(f"A quantidade deve ser inteira entre 1 e {MAX_PONTOS}.")
    return quantidade


def validar_indice_passagem(indice: int) -> tuple[str, int, int]:
    """Confirma a existência da passagem selecionada no catálogo fixo."""
    if type(indice) is not int or not 0 <= indice < len(TIPOS_PASSAGEM):
        raise ValueError("Tipo de passagem inválido.")
    return TIPOS_PASSAGEM[indice]
