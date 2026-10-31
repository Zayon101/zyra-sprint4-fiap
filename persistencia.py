"""Leitura e gravação dos dados JSON da Sprint 3 (transitório)."""

import json
from constantes import ARQUIVO_DADOS


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
        if len(lista_usuarios) > 0:
            print("Dados carregados com sucesso.")

    finally:
        if arquivo is not None:
            arquivo.close()

    return lista_usuarios
