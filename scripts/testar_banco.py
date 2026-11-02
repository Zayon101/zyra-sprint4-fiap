"""Testa a conexão com o Oracle da FIAP sem modificar o banco."""

from contextlib import closing

from zyra.database.banco import conectar


TABELAS_ESPERADAS = {"ZYRA_USUARIOS", "ZYRA_TROCAS"}


def verificar_conexao(conexao):
    """Executa uma consulta simples e verifica as tabelas do projeto."""
    with conexao.cursor() as cursor:
        cursor.execute("SELECT USER FROM DUAL")
        usuario = cursor.fetchone()[0]

        cursor.execute(
            "SELECT TABLE_NAME FROM USER_TABLES "
            "WHERE TABLE_NAME IN (:tabela_usuarios, :tabela_trocas)",
            tabela_usuarios="ZYRA_USUARIOS",
            tabela_trocas="ZYRA_TROCAS",
        )
        existentes = {linha[0] for linha in cursor.fetchall()}

    return usuario, existentes


def main():
    """Informa se a conexão está funcionando e se as tabelas existem."""
    try:
        with closing(conectar()) as conexao:
            usuario, existentes = verificar_conexao(conexao)
        print(f"[OK] Conexão estabelecida! Usuário Oracle: {usuario}")
        for tabela in sorted(TABELAS_ESPERADAS):
            print(f"[{'OK' if tabela in existentes else 'FALTA'}] {tabela}")
        if existentes != TABELAS_ESPERADAS:
            print("\nPara criar as tabelas, execute: python -m scripts.preparar_banco")
        return 0
    except (OSError, ValueError, ImportError) as erro:
        print(f"\nNão foi possível testar a conexão: {erro}")
        return 1
    except Exception as erro:
        print(f"\nFalha de conexão ou consulta no Oracle: {erro}")
        print("Verifique acesso à rede da FIAP, host, porta, SID/serviço e senha.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
