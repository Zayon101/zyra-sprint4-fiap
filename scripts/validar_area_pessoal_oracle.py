"""Validação guiada da área pessoal com Oracle real e cadastro temporário."""

from zyra.web.pessoal import ServicoPessoal
from zyra.web.servico import ServicoZyra, acesso_oracle


def main():
    print('VALIDAÇÃO DA ÁREA PESSOAL — ZYRA / ORACLE FIAP')
    print('Cria e remove um cadastro de teste. Não modifica usuários existentes.')
    if input('Digite TESTAR para continuar: ').strip() != 'TESTAR':
        print('Teste cancelado.')
        return

    id_usuario = None
    try:
        app = ServicoZyra()
        pessoal = ServicoPessoal(app)
        with acesso_oracle() as repo:
            id_usuario = repo.criar_usuario('Teste Pessoal Zyra')
        print(f'[OK] Cadastro temporário criado: ID {id_usuario}')

        codigo, dados, cookie = pessoal.processar('POST', '/api/pessoal/entrar', {'identificador': str(id_usuario)})
        token = cookie.split(';')[0].split('=', 1)[1]
        assert codigo == 200 and dados['usuario']['pontos'] == 500
        print('[OK] Identificação por ID e bônus inicial de 500')

        codigo, dados, _ = pessoal.processar('PATCH', '/api/pessoal/conta', {'nome': 'Teste Pessoal Atualizado'}, token)
        assert codigo == 200 and dados['usuario']['nome'] == 'Teste Pessoal Atualizado'
        print('[OK] Edição do próprio nome')

        with acesso_oracle() as repo:
            assert repo.adicionar_pontos(id_usuario, 100) == 600
        codigo, dados, _ = pessoal.processar('POST', '/api/pessoal/resgates', {'tipo': 1}, token)
        assert codigo == 201 and dados['usuario']['pontos'] == 13
        assert len(dados['usuario']['historico']) == 1
        print('[OK] Resgate com 600 pontos, saldo final 13')

        with acesso_oracle() as repo:
            novo = repo.consultar_usuario(id_usuario)
            assert novo['pontos'] == 13 and len(novo['historico']) == 1
        print('[OK] Saldo e histórico persistidos em outra conexão')

        codigo, dados, cookie = pessoal.processar('POST', '/api/pessoal/sair', {}, token)
        assert codigo == 200 and dados['encerrada']
        print('[OK] Sessão demonstrativa encerrada')
        print('Lote 8B.3 validado na camada de serviço e Oracle real!')
    except Exception as erro:
        print(f'[ERRO] A validação não terminou: {erro}')
        raise
    finally:
        if id_usuario is not None:
            try:
                with acesso_oracle() as repo:
                    repo.excluir_usuario(id_usuario)
                print('[OK] Cadastro temporário removido')
            except Exception as erro:
                print(f'[ATENÇÃO] Remova o cadastro temporário ID {id_usuario}: {erro}')


if __name__ == '__main__':
    main()
