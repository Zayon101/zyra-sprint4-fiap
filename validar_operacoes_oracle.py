"""Validação opt-in de pontos e passagens no Oracle real da FIAP.

Cria um único cadastro temporário, registra uma troca, confere os dados em
outra conexão e tenta excluir esse cadastro no final. Não altera os demais.
"""

from contextlib import closing

from banco import conectar
from repositorio import RepositorioOracle


def exigir(condicao, mensagem):
    """Garante a validação também ao executar Python com otimizações (-O)."""
    if not condicao:
        raise AssertionError(mensagem)


def validar():
    """Executa cenários reais com um cadastro temporário, após autorização."""
    print("TESTE DE PONTOS, PASSAGENS E HISTÓRICO — ORACLE FIAP")
    print("Um cadastro temporário será criado e removido ao final.")
    print("Outros usuários e tabelas não serão modificados.")
    if input("Digite TESTAR para autorizar: ").strip().upper() != "TESTAR":
        print("Teste cancelado. Nenhuma alteração realizada.")
        return 0

    id_temporario = None
    resultado = 1
    try:
        with closing(conectar()) as conexao:
            repositorio = RepositorioOracle(conexao)
            try:
                id_temporario = repositorio.criar_usuario("Teste Zyra Etapa Quatro")
                criado = repositorio.consultar_usuario(id_temporario)
                exigir(criado is not None and criado["pontos"] == 500, "Bônus inicial incorreto")
                print(f"[OK] Cadastro temporário criado com 500 pontos (ID {id_temporario})")

                saldo = repositorio.adicionar_pontos(id_temporario, 100)
                exigir(saldo == 600, "Crédito não atualizou o saldo para 600")
                print("[OK] Crédito de 100 pontos: saldo 600")

                sucesso, saldo = repositorio.resgatar_passagem(id_temporario, 0)
                exigir(sucesso and saldo == 13, "Resgate não produziu saldo 13")
                print("[OK] Resgate unitário (587 pontos): saldo 13")

                usuario = repositorio.consultar_usuario(id_temporario)
                exigir(usuario["pontos"] == 13, "Saldo não foi persistido")
                exigir(len(usuario["historico"]) == 1, "Histórico não contém exatamente uma troca")
                troca = usuario["historico"][0]
                exigir(troca["passagem"] == "Unitária" and troca["custo"] == 587, "Passagem ou custo incorreto")
                exigir(troca["viagens"] == 1 and troca["valor"] == 5.4, "Viagens ou valor incorretos")
                exigir(troca["id"] > 0 and troca["data"], "Identificador ou data ausente")
                print(f"[OK] Histórico registrado com data e ID da troca: #{troca['id']}")

                sucesso, saldo = repositorio.resgatar_passagem(id_temporario, 0)
                exigir(not sucesso and saldo == 13, "Resgate com saldo insuficiente não foi bloqueado")
                exigir(len(repositorio.consultar_usuario(id_temporario)["historico"]) == 1, "Resgate recusado criou troca")
                print("[OK] Segundo resgate bloqueado por saldo insuficiente, sem nova troca")

                # Consulta na segunda conexão para comprovar que os commits
                # estão disponíveis fora da conexão inicial.
                with closing(conectar()) as segunda_conexao:
                    consultado = RepositorioOracle(segunda_conexao).consultar_usuario(id_temporario)
                    exigir(consultado is not None, "Cadastro não aparece na segunda conexão")
                    exigir(consultado["pontos"] == 13, "Saldo não foi persistido entre conexões")
                    exigir(len(consultado["historico"]) == 1, "Histórico não foi persistido entre conexões")
                print("[OK] Saldo e histórico persistiram em outra conexão Oracle")
                resultado = 0
            finally:
                if id_temporario is not None:
                    try:
                        if repositorio.excluir_usuario(id_temporario):
                            print(f"[OK] Cadastro temporário ID {id_temporario} excluído")
                        else:
                            print(f"[ATENÇÃO] Não foi possível localizar o ID {id_temporario} na limpeza")
                            resultado = 1
                    except Exception as erro_limpeza:
                        print(f"[ATENÇÃO] Limpeza falhou para o ID {id_temporario}: {erro_limpeza}")
                        print("Exclua SOMENTE esse ID manualmente após verificar sua identidade.")
                        resultado = 1
    except Exception as erro:
        # A falha é exibida com a descrição do requisito que não foi cumprido.
        print(f"[ERRO] Falha de integração: {erro or 'resultado diferente do esperado'}")
        return 1
    if resultado == 0:
        print("\nEtapa 4 validada com sucesso no Oracle real!")
    return resultado


if __name__ == "__main__":
    raise SystemExit(validar())
