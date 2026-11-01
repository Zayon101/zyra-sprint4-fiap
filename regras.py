"""Validações de negócio independentes do terminal e do Oracle."""

from constantes import MAX_CARACTERES_NOME, MAX_PONTOS, TIPOS_PASSAGEM


def validar_nome_usuario(nome):
    """Normaliza o nome para persistência, respeitando o limite do banco."""
    if not isinstance(nome, str):
        raise ValueError("O nome deve ser um texto.")
    nome = nome.strip()
    if len(nome) < 3 or len(nome) > MAX_CARACTERES_NOME:
        raise ValueError(f"O nome deve ter entre 3 e {MAX_CARACTERES_NOME} caracteres.")
    return nome


def validar_saldo(pontos):
    """Valida um saldo inteiro dentro da capacidade da coluna NUMBER(12)."""
    if type(pontos) is not int or not 0 <= pontos <= MAX_PONTOS:
        raise ValueError(f"O saldo deve ser inteiro entre 0 e {MAX_PONTOS}.")
    return pontos


def validar_credito(quantidade):
    """Valida uma quantidade positiva de pontos para crédito."""
    if type(quantidade) is not int or not 1 <= quantidade <= MAX_PONTOS:
        raise ValueError(f"A quantidade deve ser inteira entre 1 e {MAX_PONTOS}.")
    return quantidade


def validar_indice_passagem(indice):
    """Confirma a existência da passagem selecionada no catálogo fixo."""
    if type(indice) is not int or not 0 <= indice < len(TIPOS_PASSAGEM):
        raise ValueError("Tipo de passagem inválido.")
    return TIPOS_PASSAGEM[indice]
