"""ZYRA — Sprint 4 | Entrada única para terminal, Oracle e página web.

Execute: python main.py
O Oracle pode reconectar automaticamente com credenciais salvas localmente.
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
from sql.conexao import (
    ARQUIVO_CONEXAO, ConfiguracaoBanco, carregar_conexao_local,
    conectar, salvar_conexao_local, excluir_conexao_local,
)
from sql.estrutura import preparar_estrutura, verificar_estrutura
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

    def _ativar_conexao(self, configuracao: ConfiguracaoBanco, nova_conexao) -> None:
        """Substitui a sessão Oracle sem deixar a web usando a conexão antiga."""
        self.encerrar_web()
        if self.conexao is not None:
            self.conexao.close()
        self.conexao = nova_conexao
        self.configuracao = configuracao
        self.repositorio = RepositorioOracle(nova_conexao)
        self.tabelas_prontas = False

    def _verificar_tabelas(self) -> None:
        """Confere colunas e restrições, não apenas a presença das tabelas."""
        if self.conexao is None:
            self.tabelas_prontas = False
            print("\nConecte ao Oracle antes de verificar as tabelas.")
            return
        try:
            diagnostico = verificar_estrutura(self.conexao)
        except Exception as erro:
            self.tabelas_prontas = False
            print(f"Não foi possível verificar a estrutura Oracle: {erro}")
            return
        for objeto, problemas in diagnostico.items():
            print(f"[{'ATENÇÃO' if problemas else 'OK'}] {objeto}")
            for problema in problemas:
                print(f"    - {problema}")
        self.tabelas_prontas = all(not problemas for problemas in diagnostico.values())
        if not self.tabelas_prontas:
            print("Estrutura incompleta ou incompatível. Consulte [7] para preparar objetos ausentes.")
            print("Tabelas existentes incorretas não serão alteradas automaticamente.")

    def conectar_automaticamente(self) -> None:
        """Tenta reconectar a configuração salva sem impedir a abertura do menu."""
        self._conectar_salva(automatico=True)

    def _conectar_salva(self, automatico: bool = False) -> None:
        """Reutiliza a conexão salva, sob demanda ou na inicialização."""
        try:
            configuracao = carregar_conexao_local()
        except ValueError as erro:
            print(f"\n[AVISO] {erro} Use [7] para corrigir ou excluir o arquivo.")
            return
        if configuracao is None:
            if not automatico:
                print("\nNão existe conexão salva. Escolha [1] para informar credenciais.")
            return
        print(f"\nTentando conectar ao Oracle com a configuração salva ({configuracao.usuario})...")
        try:
            nova_conexao = conectar(configuracao)
        except Exception as erro:
            print(f"[AVISO] Não foi possível usar a conexão salva: {erro}")
            print("O menu continua disponível; escolha [1] para atualizar as credenciais.")
            return
        self._ativar_conexao(configuracao, nova_conexao)
        print(f"[OK] Conectado ao Oracle: {configuracao.usuario}.")
        self._verificar_tabelas()

    def _conectar_nova(self) -> None:
        """Troca a sessão atual e oferece manter, substituir ou apagar as credenciais salvas."""
        try:
            configuracao = solicitar_configuracao()
            nova_conexao = conectar(configuracao)
        except Exception as erro:
            print(f"\nNão foi possível conectar ao Oracle: {erro}")
            return
        self._ativar_conexao(configuracao, nova_conexao)
        print(f"\n[OK] Conexão estabelecida com o usuário {configuracao.usuario}.")
        print("Salvar a conexão também salva a senha em texto simples neste computador.")
        try:
            if confirmou("Salvar esta conexão para as próximas execuções? [s/N]: "):
                try:
                    salvar_conexao_local(configuracao)
                except OSError as erro:
                    print(f"Não foi possível salvar a configuração: {erro}")
                else:
                    print(f"[OK] Conexão salva: {ARQUIVO_CONEXAO.name}.")
            elif ARQUIVO_CONEXAO.exists():
                print("Existe uma configuração ANTERIOR salva, diferente da conexão ativa.")
                if confirmou("Deseja EXCLUIR a configuração antiga salva? [s/N]: "):
                    self._apagar_configuracao_salva(confirmar=False)
                else:
                    print("Configuração anterior mantida; será usada no próximo início.")

            if confirmou("Criar/verificar as tabelas agora? [s/N]: "):
                self._preparar_tabelas(confirmar=False)
            else:
                self._verificar_tabelas()
        except (KeyboardInterrupt, EOFError):
            print("\nConfiguração opcional interrompida; conexão atual mantida.")
            self._verificar_tabelas()

    def _apagar_configuracao_salva(self, confirmar: bool = True) -> None:
        """Remove credenciais no disco, preservando a conexão atual em memória."""
        if confirmar and not confirmou("Apagar as credenciais salvas em disco? [s/N]: "):
            print("Exclusão cancelada.")
            return
        try:
            excluida = excluir_conexao_local()
        except OSError as erro:
            print(f"Não foi possível apagar a configuração: {erro}")
        else:
            if excluida:
                print("[OK] Configuração salva apagada. A conexão atual continua ativa.")
            else:
                print("Não há configuração salva para apagar.")

    def _preparar_tabelas(self, confirmar: bool = True) -> None:
        """Cria objetos ausentes sem alterar tabelas existentes."""
        if self.conexao is None:
            print("\nConecte ao Oracle antes de preparar as tabelas.")
            return
        if confirmar and not confirmou("Criar somente tabelas e índices AUSENTES? [s/N]: "):
            print("Criação cancelada.")
            return
        try:
            preparar_estrutura(self.conexao)
        except Exception as erro:
            print(f"\nFalha ao preparar a estrutura: {erro}")
            print("Confira as permissões CREATE TABLE e CREATE INDEX do seu usuário.")
        self._verificar_tabelas()

    def conectar_sql(self) -> None:
        """Submenu de gerenciamento das configurações e das tabelas."""
        while True:
            print("\n" + "=" * 45)
            print("           SQL / CONEXÕES ORACLE")
            print("=" * 45)
            print("[1] Conectar / trocar credenciais")
            print("[2] Reutilizar conexão salva")
            print("[3] Apagar conexão salva")
            print("[4] Criar/verificar tabelas na conexão ATUAL")
            print("[5] Diagnosticar estrutura atual")
            print("[0] Voltar")
            print(f"Conexão atual: {self.configuracao.usuario if self.configuracao else 'nenhuma'}")
            print(f"Conexão salva: {'sim' if ARQUIVO_CONEXAO.exists() else 'não'}")
            try:
                escolha = input("Escolha uma opção: ").strip()
                if escolha == "0":
                    return
                if escolha == "1":
                    self._conectar_nova()
                elif escolha == "2":
                    self._conectar_salva()
                elif escolha == "3":
                    self._apagar_configuracao_salva()
                elif escolha == "4":
                    self._preparar_tabelas()
                elif escolha == "5":
                    self._verificar_tabelas()
                else:
                    print("Opção inválida.")
            except (KeyboardInterrupt, EOFError):
                print("\nRetornando ao menu principal.")
                return

    def repositorio_ativo(self) -> RepositorioOracle | None:
        """Bloqueia apenas operações que dependem das tabelas SQL."""
        if self.repositorio is None or not self.tabelas_prontas:
            print("\nBanco não preparado. Use [7] Conectar SQL / preparar tabelas.")
            return None
        return self.repositorio

    def abrir_web(self) -> None:
        """Inicia o servidor mesmo sem Oracle; as rotas SQL retornarão 503."""
        if self.servidor is None:
            configuracao = self.configuracao
            banco_disponivel = configuracao is not None and self.tabelas_prontas

            @contextmanager
            def repositorio_http():
                if not banco_disponivel:
                    raise ErroBanco("Banco Oracle não configurado ou tabelas incompatíveis.")
                # Uma nova conexão por requisição evita compartilhar sessões entre threads.
                conexao = conectar(configuracao)
                try:
                    yield RepositorioOracle(conexao)
                finally:
                    conexao.close()

            try:
                servico = ServicoZyra(
                    repositorio_factory=repositorio_http,
                    banco_disponivel=banco_disponivel,
                )
                self.servidor = criar_servidor(
                    porta=8765, servico=servico, banco_disponivel=banco_disponivel
                )
                self.thread_web = Thread(target=self.servidor.serve_forever, daemon=True)
                self.thread_web.start()
            except OSError as erro:
                self.servidor = None
                print(f"\nNão foi possível iniciar a página web: {erro}")
                return
            print("\n[OK] Servidor web iniciado.")
            if not banco_disponivel:
                print("[AVISO] Sem Oracle preparado: página, clima e passagens disponíveis;")
                print("        consultas e alterações de usuários retornarão HTTP 503.")
                print("        Após conectar pelo menu [7], reabra a web pelo [8].")
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
            self.conectar_automaticamente()
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
