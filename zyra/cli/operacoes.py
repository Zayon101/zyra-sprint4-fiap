"""Pontos, passagens, histórico e estatísticas usando o banco Oracle."""

from zyra.core.constantes import TIPOS_PASSAGEM, VALOR_PASSAGEM, VALOR_POR_PONTO
from zyra.core.relatorios import calcular_resumo
from zyra.cli.utils import formatar_data_troca, formatar_reais, pausar, validar_numero


def escolher_usuario(repositorio):
    """Escolhe um usuário válido e retorna seu dicionário ou None."""
    usuarios = repositorio.listar_usuarios(incluir_historico=False)
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return None
    if len(usuarios) == 1:
        usuario = usuarios[0]
        print(f"\nUsuário selecionado automaticamente: ID {usuario['id']} - {usuario['nome']}")
        return repositorio.consultar_usuario(usuario["id"])

    for usuario in usuarios:
        print(f"ID {usuario['id']} - {usuario['nome']}")
    while True:
        id_usuario = validar_numero("\nDigite o ID do usuário: ")
        usuario = repositorio.consultar_usuario(id_usuario)
        if usuario is not None:
            return usuario
        print("Erro: usuário inválido.")


def adicionar_pontos(repositorio):
    """Soma pontos usando UPDATE no Oracle."""
    usuario = escolher_usuario(repositorio)
    if usuario is None:
        pausar()
        return
    print("\n" + "=" * 40)
    print("           ADICIONAR PONTOS")
    print("=" * 40)
    pontos = 0
    while pontos <= 0:
        pontos = validar_numero("\nDigite a quantidade de pontos: ")
        if pontos <= 0:
            print("Informe um valor maior que zero.")
    saldo = repositorio.adicionar_pontos(usuario["id"], pontos)
    if saldo is None:
        print("Usuário não encontrado.")
    else:
        print("\nPontos adicionados com sucesso!")
        print(f"Novo saldo: {saldo} pontos")
        print(f"Saldo em reais: {formatar_reais(saldo * VALOR_POR_PONTO)}")
    pausar()


def mostrar_passagens() -> None:
    """Exibe a tabela fixa de passagens (não depende do banco)."""
    print("\n" + "=" * 40)
    print("           PASSAGENS DISPONÍVEIS")
    print("=" * 40)
    for indice, (nome, viagens, custo) in enumerate(TIPOS_PASSAGEM, start=1):
        print(
            f"[{indice}] {nome} | {viagens} viagem(ns) | {custo} pontos | "
            f"{formatar_reais(viagens * VALOR_PASSAGEM)}"
        )


def trocar_pontos_por_passagem(repositorio):
    """Realiza troca e salva saldo e histórico numa transação Oracle."""
    usuario = escolher_usuario(repositorio)
    if usuario is None:
        pausar()
        return
    print("\n" + "=" * 40)
    print("           TROCA DE PONTOS")
    print("=" * 40)
    mostrar_passagens()
    opcao = 0
    while not 1 <= opcao <= len(TIPOS_PASSAGEM):
        opcao = validar_numero("\nEscolha a passagem desejada: ")
        if not 1 <= opcao <= len(TIPOS_PASSAGEM):
            print("Erro: opção inválida.")

    sucesso, saldo = repositorio.resgatar_passagem(usuario["id"], opcao - 1)
    if sucesso:
        print("\nTroca realizada com sucesso!")
        print(f"Passagem adquirida: {TIPOS_PASSAGEM[opcao - 1][0]}")
        print(f"Saldo atual: {saldo} pontos")
    elif saldo is None:
        print("Usuário não encontrado.")
    else:
        print("\nSaldo insuficiente.")
        print(f"Saldo atual: {saldo} pontos")
        print(f"Faltam: {max(0, TIPOS_PASSAGEM[opcao - 1][2] - saldo)} pontos")
    pausar()


def historico_trocas(repositorio):
    """Consulta as trocas armazenadas no Oracle para o usuário escolhido."""
    usuario = escolher_usuario(repositorio)
    if usuario is None:
        pausar()
        return
    print("\n" + "=" * 40)
    print("           HISTÓRICO DE TROCAS")
    print("=" * 40)
    if not usuario["historico"]:
        print("\nNenhuma troca realizada.")
    else:
        print(f"\nHistórico de {usuario['nome']}:")
        for troca in usuario["historico"]:
            print(
                f"[✓] {troca['passagem']} | {troca['viagens']} viagem(ns) | "
                f"{troca['custo']} pontos | {formatar_reais(troca['valor'])}"
            )
            print(f"    Resgate #{troca['id']} em {formatar_data_troca(troca['data'])}")
    pausar()


def resumo_sistema(repositorio):
    """Exibe indicadores de usuários e trocas consultados no Oracle."""
    resumo = calcular_resumo(repositorio.listar_usuarios())
    print("\n" + "=" * 40)
    print("           RESUMO DO SISTEMA")
    print("=" * 40)
    print(f"Total de usuários: {resumo['total_usuarios']}")
    print(f"Total de pontos: {resumo['total_pontos']}")
    print(f"Valor total em saldo: {formatar_reais(resumo['valor_total_saldo_reais'])}")
    print(f"Total de trocas: {resumo['total_trocas']}")
    print(f"Total de viagens resgatadas: {resumo['total_viagens']}")
    print(f"Valor total resgatado: {formatar_reais(resumo['valor_total_resgatado_reais'])}")
    pausar()
