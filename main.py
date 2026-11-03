"""ZYRA — Sprint 4 | Entrada única para terminal, Oracle e página web.

Execute: python main.py
O acesso ao Oracle é configurado interativamente, sem gravar senhas.
"""

from contextlib import contextmanager
from getpass import getpass
from threading import Thread
import webbrowser

from api.clima import CatalogoClima
from api.servidor import criar_servidor
from api.servico import ServicoZyra
from sistema.clima import menu_clima
from sistema.menus import exibir_boas_vindas, exibir_menu, menu_crud, menu_exportacao, menu_operacoes
from sistema.operacoes import historico_trocas, resumo_sistema
from sql.conexao import ConfiguracaoBanco, conectar
from sql.estrutura import preparar_estrutura, situacao_tabelas
from sql.repositorio import ErroBanco, RepositorioOracle

ENDERECO_WEB = "http://127.0.0.1:8765/"


def solicitar_configuracao() -> ConfiguracaoBanco:
    """Pergunta as credenciais do próprio esquema Oracle do usuário."""
    print("\n" + "=" * 45)
    print("              CONECTAR SQL")
    print("=" * 45)
    print("Utilize as mesmas informações da conexão do SQL Developer.")
    usuario = input("Usuário Oracle: ").strip()
    senha = getpass("Senha Oracle (oculta): ")
    host = input("Servidor / host: ").strip()
    porta_texto = input("Porta [1521]: ").strip() or "1521"
    try:
        porta = int(porta_texto)
    except ValueError as erro:
        raise ValueError("Informe uma porta numérica válida.") from erro
    if not 1 <= porta <= 65535:
        raise ValueError("A porta deve estar entre 1 e 65535.")

    print("\nTipo de conexão: [1] SID  [2] Nome do serviço")
    escolha = input("Selecione 1 ou 2: ").strip()
    if escolha not in ("1", "2"):
        raise ValueError("Tipo de conexão inválido. Use 1 ou 2.")
    identificador = input("Informe o SID: " if escolha == "1" else "Informe o nome do serviço: ").strip()
    if not usuario or not senha or not host or not identificador:
        raise ValueError("Usuário, senha, host e identificador são obrigatórios.")

    return ConfiguracaoBanco(
        usuario=usuario, senha=senha, host=host, porta=porta,
        sid=identificador if escolha == "1" else "",
        servico=identificador if escolha == "2" else "",
    )


def confirmou(pergunta: str) -> bool:
    """Somente uma resposta afirmativa explícita autoriza criar objetos."""
    return input(pergunta).strip().casefold() in ("s", "sim")


class Zyra:
    """Controla a conexão SQL e a instância local do servidor web."""

    def __init__(self) -> None:
        self.conexao = None
        self.configuracao: ConfiguracaoBanco | None = None
        self.repositorio: RepositorioOracle | None = None
        self.tabelas_prontas = False
        self.servidor = None
        self.thread_web: Thread | None = None
        self.clima = CatalogoClima()

    def conectar_sql(self) -> None:
        """Testa credenciais, conserva a conexão anterior se a nova falhar."""
        try:
            configuracao = solicitar_configuracao()
            nova_conexao = conectar(configuracao)
        except Exception as erro:
            print(f"\nNão foi possível conectar ao Oracle: {erro}")
            return

        # A troca de conexão não deve deixar o servidor apontando para o banco antigo.
        self.encerrar_web()
        if self.conexao is not None:
            self.conexao.close()
        self.conexao = nova_conexao
        self.configuracao = configuracao
        self.repositorio = RepositorioOracle(nova_conexao)
        print(f"\n[OK] Conexão estabelecida com o usuário {configuracao.usuario}.")
        print("As credenciais ficam somente na memória durante esta execução.")

        if confirmou("Deseja criar/verificar as tabelas Zyra agora? [s/N]: "):
            try:
                preparar_estrutura(self.conexao)
            except Exception as erro:
                print(f"\nFalha ao preparar as tabelas: {erro}")
                print("Verifique as permissões CREATE TABLE e CREATE INDEX do seu usuário.")
        try:
            situacao = situacao_tabelas(self.conexao)
            for tabela, existe in situacao.items():
                print(f"[{'OK' if existe else 'FALTA'}] {tabela}")
            self.tabelas_prontas = all(situacao.values())
            if not self.tabelas_prontas:
                print("Para usar o CRUD, conecte novamente e autorize a criação das tabelas.")
        except Exception as erro:
            self.tabelas_prontas = False
            print(f"Não foi possível confirmar a estrutura: {erro}")

    def repositorio_ativo(self) -> RepositorioOracle | None:
        """Bloqueia apenas operações que dependem das tabelas SQL."""
        if self.repositorio is None or not self.tabelas_prontas:
            print("\nBanco não preparado. Use [7] Conectar SQL / preparar tabelas.")
            return None
        return self.repositorio

    def abrir_web(self) -> None:
        """Inicia a API e abre a página web, sem precisar de React instalado."""
        if self.repositorio_ativo() is None:
            return
        if self.servidor is None:
            # Nova conexão por requisição: a instância do menu não é compartilhada entre threads.
            configuracao = self.configuracao

            @contextmanager
            def repositorio_http():
                conexao = conectar(configuracao)
                try:
                    yield RepositorioOracle(conexao)
                finally:
                    conexao.close()

            try:
                servico = ServicoZyra(repositorio_factory=repositorio_http)
                self.servidor = criar_servidor(porta=8765, servico=servico)
                self.thread_web = Thread(target=self.servidor.serve_forever, daemon=True)
                self.thread_web.start()
            except OSError as erro:
                self.servidor = None
                print(f"\nNão foi possível iniciar a página web: {erro}")
                return
            print("\n[OK] Servidor web iniciado.")
        else:
            print("\nO servidor web já está funcionando.")
        print(f"Acesse: {ENDERECO_WEB}")
        try:
            if not webbrowser.open_new_tab(ENDERECO_WEB):
                print("Abra o endereço acima manualmente no navegador.")
        except Exception:
            print("Abra o endereço acima manualmente no navegador.")

    def encerrar_web(self) -> None:
        """Encerra o servidor HTTP antes de trocar de conexão ou sair."""
        if self.servidor is not None:
            self.servidor.shutdown()
            self.servidor.server_close()
            if self.thread_web is not None:
                self.thread_web.join(timeout=3)
            self.servidor = None
            self.thread_web = None

    def encerrar(self) -> None:
        self.encerrar_web()
        if self.conexao is not None:
            self.conexao.close()
            self.conexao = None

    def executar(self) -> None:
        """Menu principal da Sprint 3 com SQL e web como novas opções."""
        try:
            exibir_boas_vindas()
            while True:
                exibir_menu()
                print("[SQL: conectado]" if self.tabelas_prontas else "[SQL: não preparado]")
                if self.servidor is not None:
                    print("[WEB: ativa em 127.0.0.1:8765]")
                try:
                    opcao = int(input("Escolha uma opção: "))
                except ValueError:
                    print("\nErro: digite apenas números.")
                    continue
                try:
                    if opcao == 0:
                        print("\nPrograma finalizado. Obrigado por utilizar a Zyra!")
                        break
                    if opcao == 7:
                        self.conectar_sql()
                    elif opcao == 8:
                        self.abrir_web()
                    elif opcao == 6:
                        menu_clima(self.clima)
                    elif opcao in (1, 2, 3, 4, 5):
                        repositorio = self.repositorio_ativo()
                        if repositorio is None:
                            continue
                        match opcao:
                            case 1: menu_crud(repositorio)
                            case 2: menu_operacoes(repositorio)
                            case 3: historico_trocas(repositorio)
                            case 4: resumo_sistema(repositorio)
                            case 5: menu_exportacao(repositorio)
                    else:
                        print("\nOpção inválida.")
                except (ValueError, ErroBanco) as erro:
                    print(f"\nNão foi possível concluir a operação: {erro}")
        except (KeyboardInterrupt, EOFError):
            print("\nExecução encerrada pelo usuário.")
        finally:
            self.encerrar()


def main() -> None:
    Zyra().executar()


if __name__ == "__main__":
    main()
