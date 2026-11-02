"""Teste manual da API HTTP do Zyra contra o Oracle real da FIAP.

Cria apenas um cadastro temporário após confirmação, executa consultas,
crédito e resgate, e o apaga ao final. Não consulta a Open-Meteo.
"""

import json
from http.client import HTTPConnection
from threading import Thread

from banco import conectar
from repositorio import RepositorioOracle
from servidor_web import criar_servidor


def requisitar(porta, metodo, rota, dados=None):
    """Executa uma requisição JSON para a API local e devolve (status, corpo)."""
    conexao = HTTPConnection("127.0.0.1", porta, timeout=20)
    headers = {"Accept": "application/json"}
    if metodo != "GET":
        headers["X-Zyra-Cliente"] = "painel-web"
    corpo = None
    if dados is not None:
        corpo = json.dumps(dados).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        conexao.request(metodo, rota, body=corpo, headers=headers)
        resposta = conexao.getresponse()
        return resposta.status, json.loads(resposta.read().decode("utf-8"))
    finally:
        conexao.close()


def confirmar(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)
    print(f"[OK] {mensagem}")


def main():
    print("VALIDAÇÃO DA INTEGRAÇÃO WEB — ZYRA / ORACLE FIAP")
    print("Este teste criará e removerá um usuário temporário no banco configurado no .env.")
    print("O programa NÃO modifica outros cadastros.")
    if input("Digite TESTAR para continuar: ").strip() != "TESTAR":
        print("Teste cancelado.")
        return
    servidor = None
    thread = None
    id_usuario = None
    try:
        servidor = criar_servidor(0)
        porta = servidor.server_address[1]
        thread = Thread(target=servidor.serve_forever, daemon=True)
        thread.start()

        codigo, dados = requisitar(porta, "GET", "/api/status")
        confirmar(codigo == 200 and dados["status"] == "ok", "Servidor HTTP local responde")

        codigo, dados = requisitar(porta, "POST", "/api/usuarios", {"nome": "Teste Web Zyra"})
        confirmar(codigo == 201, "CREATE via HTTP")
        id_usuario = dados["usuario"]["id"]
        confirmar(dados["usuario"]["pontos"] == 500, "Bônus inicial de 500 pontos")

        codigo, dados = requisitar(porta, "GET", f"/api/usuarios/{id_usuario}")
        confirmar(codigo == 200 and dados["usuario"]["nome"] == "Teste Web Zyra", "READ via HTTP")

        codigo, dados = requisitar(porta, "PATCH", f"/api/usuarios/{id_usuario}", {"nome": "Teste Web Atualizado"})
        confirmar(codigo == 200 and dados["usuario"]["nome"] == "Teste Web Atualizado", "UPDATE via HTTP")

        codigo, dados = requisitar(porta, "POST", f"/api/usuarios/{id_usuario}/pontos", {"quantidade": 100})
        confirmar(codigo == 200 and dados["usuario"]["pontos"] == 600, "Crédito via HTTP: saldo de 600")

        codigo, dados = requisitar(porta, "POST", f"/api/usuarios/{id_usuario}/resgates", {"tipo": 1})
        confirmar(codigo == 201 and dados["usuario"]["pontos"] == 13, "Resgate via HTTP: saldo de 13")
        confirmar(len(dados["usuario"]["historico"]) == 1, "Troca registrada via HTTP")

        codigo, _ = requisitar(porta, "POST", f"/api/usuarios/{id_usuario}/resgates", {"tipo": 1})
        confirmar(codigo == 409, "Saldo insuficiente bloqueia outra troca")

        conexao = conectar()
        try:
            usuario_oracle = RepositorioOracle(conexao).consultar_usuario(id_usuario)
            confirmar(usuario_oracle["pontos"] == 13 and len(usuario_oracle["historico"]) == 1,
                      "Saldo e histórico conferidos em outra conexão Oracle")
        finally:
            conexao.close()

        codigo, dados = requisitar(porta, "DELETE", f"/api/usuarios/{id_usuario}")
        confirmar(codigo == 200 and dados["excluido"], "DELETE via HTTP")
        id_usuario = None
        print("\nLote 7 validado: API HTTP e Oracle compartilham os mesmos dados!")
    except Exception as erro:
        print(f"\n[ERRO] Falha na validação: {erro}")
        print("Confira se o Oracle está acessível e se o .env está correto.")
    finally:
        if id_usuario is not None:
            try:
                conexao = conectar()
                try:
                    if RepositorioOracle(conexao).excluir_usuario(id_usuario):
                        print(f"[LIMPEZA] Usuário temporário ID {id_usuario} removido.")
                finally:
                    conexao.close()
            except Exception as erro:
                print(f"[ATENÇÃO] Não foi possível limpar o usuário temporário ID {id_usuario}: {erro}")
                print("Remova-o manualmente pelo menu de usuários, se necessário.")
        if servidor is not None:
            servidor.shutdown()
            servidor.server_close()
        if thread is not None:
            thread.join(timeout=3)


if __name__ == "__main__":
    main()
