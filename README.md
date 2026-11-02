# Zyra — Sprint 4 | Lote 8C: organização do backend

Sistema acadêmico que simula a conversão de pontos SoulUp em passagens de metrô. O Oracle da FIAP é a fonte principal dos dados para o terminal e para a API HTTP local. A Open-Meteo fornece informações climáticas para auxiliar no planejamento de viagens.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Estrutura

```text
zyra-sprint4-fiap/
├── main.py                    # Inicia a interface de terminal
├── servidor_web.py            # Inicia o painel HTTP local
├── zyra/
│   ├── cli/                   # Menus, entradas e operações no terminal
│   │   ├── app.py
│   │   ├── menus.py
│   │   ├── usuarios.py
│   │   ├── operacoes.py
│   │   ├── clima.py
│   │   └── utils.py
│   ├── core/                  # Regras de negócio e estatísticas
│   │   ├── constantes.py
│   │   ├── regras.py
│   │   └── relatorios.py
│   ├── database/              # Conexão e persistência Oracle
│   │   ├── banco.py
│   │   └── repositorio.py
│   ├── integrations/          # Integração externa Open-Meteo
│   │   └── api_clima.py
│   ├── web/                   # API HTTP e serviço web
│   │   ├── servidor.py
│   │   └── servico.py
│   └── exportacao.py           # Exportação das consultas em JSON
├── scripts/                   # Preparação, migração e diagnósticos
├── sql/                       # DDL do Oracle
│   └── criar_tabelas.sql
├── painel_web/                # Painel de demonstração independente
├── integracao_react/          # Exemplo para consumir a API no React
├── tests/                     # Testes automatizados e banco simulado
├── requirements.txt
├── .env.example
└── .gitignore
```

**O que mudou no Lote 8C:** organização em pacotes, imports absolutos, localização correta do `.env`, do SQL, do painel e dos arquivos exportados, e atualização dos comandos dos scripts. **Não foram alterados** os endpoints HTTP, os valores de pontos, o modelo das tabelas ou as regras de transações. O painel de demonstração também foi preservado.

## Como atualizar seu projeto

1. **Salve uma cópia da pasta atual** ou faça commit/backup antes da substituição.
2. Extraia o pacote em uma **nova pasta**. Não sobreponha o conteúdo à estrutura antiga: arquivos que mudaram de lugar poderiam ficar duplicados.
3. Copie apenas seu arquivo `.env` anterior para a **raiz da pasta nova**; não compartilhe suas credenciais.
4. Instale as dependências, se necessário: `python -m pip install -r requirements.txt`.
5. Abra um terminal **na raiz do projeto** para executar os comandos seguintes.
6. Se os testes passarem e o banco estiver acessível, substitua sua pasta de trabalho, removendo os arquivos antigos do Git com `git add -A`.

## Execução

| Ação | Comando (na raiz) |
|---|---|
| Testes automatizados | `python -m unittest discover -s tests -v` |
| Diagnóstico de conexão Oracle | `python -m scripts.testar_banco` |
| Programa em terminal | `python main.py` |
| Servidor e painel HTTP local | `python servidor_web.py` |
| Testar API Open-Meteo | `python -m scripts.validar_api_clima` |
| Validar CRUD no Oracle real | `python -m scripts.validar_crud_oracle` |
| Validar pontos/resgates | `python -m scripts.validar_operacoes_oracle` |
| Validar exportação JSON | `python -m scripts.validar_exportacao_oracle` |
| Validar HTTP + Oracle real | `python -m scripts.validar_web_oracle` |
| Importar JSON da Sprint 3 (opcional) | `python -m scripts.importar_json` |
| Preparar esquema Oracle (apenas se necessário) | `python -m scripts.preparar_banco` |

**Atenção:** o Oracle já foi preparado e testado nas etapas anteriores. Não é necessário recriar as tabelas. Os scripts de validação do Oracle podem criar dados temporários; leia os avisos antes de confirmar.

O painel de demonstração permanece em `http://127.0.0.1:8765/`, com as mesmas rotas `/api/...`. Ao receber o front-end React real, usaremos o exemplo `integracao_react/zyraApi.ts` como referência para conectar as páginas. O front-end oficial **ainda não foi integrado**.

## Segurança e escopo

- O `.env` deve ficar na raiz e **nunca** ser publicado no GitHub nem enviado no ZIP.
- O servidor HTTP está restrito a `127.0.0.1` e não implementa autenticação real. O cabeçalho `X-Zyra-Cliente` não substitui autenticação. Não o exponha à internet ou a uma rede sem proteção adequada.
- O painel de demonstração acessa e modifica dados do Oracle. Para testes, utilize usuários fictícios.
- A escolha de usuário por nome/ID sem senha, planejada para o futuro front-end, **não autentica ninguém**. Antes de liberar funções administrativas ou dados privados a usuários reais, o backend precisará validar identidades e permissões.
- O arquivo `programa_sprint3_original.py` foi retirado do pacote ativo porque é apenas uma duplicação histórica. Ele continua disponível no ZIP e/ou histórico da Sprint 3. Nenhuma funcionalidade depende desse arquivo.

## Regressão

O refactor mantém a suíte de testes das etapas anteriores e acrescenta verificações de caminhos e pontos de entrada. Testes locais com Oracle simulado não substituem a validação na conexão real da FIAP. Execute o comando `python -m scripts.validar_web_oracle` para conferir a integração após a reorganização; ele precisa das suas credenciais e acesso ao banco.

## Atualização no mesmo repositório Git

Se você mantiver seu projeto Git atual, copie os novos arquivos para ele **preservando `.git` e `.env`**. Remova os módulos antigos da raiz (por exemplo, `banco.py`, `repositorio.py`, `menus.py`, `operacoes.py`, `api_clima.py`, `servico_web.py`, os `validar_*.py`, `importar_json.py`, `testar_banco.py`, `preparar_banco.py` e o SQL antigo da raiz), pois foram movidos para pacotes. Também remova a cópia `programa_sprint3_original.py` do pacote ativo; ela é histórica.

Execute `git status` para conferir os arquivos movidos, depois `git add -A` e `git diff --cached --stat` para revisar o commit antes de registrá-lo. O Git pode detectar esses movimentos como renomeações; isso é esperado. Não inclua `.env` ou arquivos JSON exportados.
