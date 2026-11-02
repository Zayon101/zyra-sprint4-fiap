"""Teste opt-in de CRUD no Oracle real.

Cria um único usuário de teste, confirma as operações e o remove ao final.
Não execute sem conhecer o banco conectado e sem autorizar o teste.
"""

from zyra.database.banco import conectar
from zyra.database.repositorio import RepositorioOracle


def validar_crud(repositorio):
    """Executa os quatro verbos CRUD em um cadastro temporário."""
    id_teste = None
    try:
        id_teste = repositorio.criar_usuario("Teste Zyra Sprint")
        print(f"[OK] CREATE - usuário temporário: ID {id_teste}")

        criado = repositorio.consultar_usuario(id_teste)
        assert criado is not None and criado["pontos"] == 500
        print("[OK] READ - cadastro e bônus consultados no Oracle")

        assert repositorio.alterar_nome(id_teste, "Teste Zyra Atualizado")
        assert repositorio.alterar_pontos(id_teste, 700)
        atualizado = repositorio.consultar_usuario(id_teste)
        assert atualizado["nome"] == "Teste Zyra Atualizado"
        assert atualizado["pontos"] == 700
        print("[OK] UPDATE - nome e pontos alterados")

        assert repositorio.excluir_usuario(id_teste)
        id_teste = None
        print("[OK] DELETE - cadastro temporário excluído")
        print("\nCRUD Oracle validado com sucesso!")
    finally:
        if id_teste is not None:
            print(f"Limpando cadastro temporário (ID {id_teste})...")
            try:
                repositorio.excluir_usuario(id_teste)
                print("[OK] Cadastro temporário removido")
            except Exception as erro:
                print(f"[ATENÇÃO] Limpeza não concluída. Verifique o ID {id_teste}: {erro}")


def main():
    print("Este teste fará INSERT, SELECT, UPDATE e DELETE em um usuário novo")
    print("na conexão configurada em seu arquivo .env. Não altera outros cadastros.")
    if input("Digite TESTAR para autorizar: ").strip() != "TESTAR":
        print("Teste cancelado.")
        return
    try:
        conexao = conectar()
    except Exception as erro:
        print(f"Falha ao conectar: {erro}")
        return
    try:
        validar_crud(RepositorioOracle(conexao))
    except Exception as erro:
        print(f"\nFalha no teste de integração: {erro}")
        if erro.__cause__ is not None:
            print(f"Detalhes técnicos: {erro.__cause__}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
