# Zyra — Sprint 4 | Backend Python

Sistema acadêmico da FIAP que simula a conversão de pontos SoulUp em passagens de metrô. O **Oracle da FIAP** é a fonte principal dos usuários, saldos e históricos. A API HTTP local permite que o front-end React, mantido em **outro repositório**, consulte e altere os mesmos dados. A Open-Meteo oferece uma consulta adicional de condições climáticas.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Organização

```text
zyra-sprint4-fiap/
├── main.py                    # Entrada da interface de terminal
├── servidor_web.py            # Entrada da API HTTP local
├── zyra/
│   ├── cli/                   # Menus, formulários e apresentação no terminal
│   ├── core/                  # Constantes, validações, modelos tipados e relatórios
│   ├── database/              # Configuração e repositório SQL do Oracle
│   ├── integrations/          # Consumo da API Open-Meteo
│   ├── web/                   # API HTTP e sessões pessoais demonstrativas
│   └── exportacao.py          # Exportação de consultas SQL para JSON
├── scripts/                   # Preparação, importação e validadores manuais
├── sql/                       # Script de criação do esquema Oracle
├── tests/                     # Testes por funcionalidade + Oracle simulado
├── examples/
│   ├── painel_web/            # Demonstração HTML independente (opcional)
│   └── integracao_react/      # Exemplo histórico de cliente TypeScript (opcional)
├── requirements.txt
├── .env.example
└── .gitignore
```

A estrutura tipada dos dados está em `zyra/core/modelos.py`. A regra de nomes é compartilhada entre terminal, API HTTP e importação de JSON: de 3 a 120 caracteres, com letras Unicode, espaços, hífens e apóstrofos. O catálogo de passagens e os valores simulados permanecem inalterados.

## Preparação local

1. Use Python 3.11 ou superior (os testes foram executados em Python 3.14).
2. Na raiz do repositório, execute `python -m pip install -r requirements.txt`.
3. Copie `.env.example` para `.env` e configure o acesso ao Oracle. **Nunca publique ou envie o `.env` preenchido.**
4. Se a estrutura do banco já existir na FIAP, **não é necessário** executar o criador de tabelas.

## Comandos

| Objetivo | Comando |
|---|---|
| Testes automatizados locais | `python -m unittest discover -s tests -v` |
| Iniciar terminal | `python main.py` |
| Iniciar API HTTP e painel opcional | `python servidor_web.py` |
| Verificar Oracle | `python -m scripts.testar_banco` |
| Validar CRUD no Oracle real | `python -m scripts.validar_crud_oracle` |
| Validar pontos e trocas | `python -m scripts.validar_operacoes_oracle` |
| Validar JSON | `python -m scripts.validar_exportacao_oracle` |
| Validar API HTTP + Oracle | `python -m scripts.validar_web_oracle` |
| Validar área pessoal + Oracle | `python -m scripts.validar_area_pessoal_oracle` |
| Testar Open-Meteo | `python -m scripts.validar_api_clima` |
| Importar JSON antigo (opcional) | `python -m scripts.importar_json` |
| Criar tabelas ausentes (somente se necessário) | `python -m scripts.preparar_banco` |

Os testes automatizados executados localmente usam um **adaptador SQLite que simula parte das operações Oracle**. Isso não substitui os testes de integração com o servidor real da FIAP. Os validadores podem criar e remover usuários temporários: leia as mensagens de confirmação antes de autorizá-los.

## Comunicação com o front-end

- Backend: `http://127.0.0.1:8765`; executado com `python servidor_web.py`.
- Front-end React/Vite: normalmente `http://localhost:5173`, usando proxy local `/api` para o backend.
- CRUD, crédito de pontos, resgate, histórico, resumo, clima e acesso pessoal são atendidos pela API existente. **Não houve mudança nos contratos HTTP nesta revisão.**
- O painel HTML em `http://127.0.0.1:8765/` ainda funciona, mas é apenas um exemplo. O React real fica no seu repositório separado.

**Escopo acadêmico local:** a seleção de cadastro por nome ou ID não comprova identidade; as rotas administrativas não têm autenticação. Não exponha esse backend à internet. A API Trilhos da ARTESP ainda não foi adicionada; a integração externa ativa é a Open-Meteo.

## Persistência, consultas e exportações

- As operações SQL utilizam parâmetros vinculados, e os resgates descontam pontos e registram trocas na mesma transação.
- `RepositorioOracle.listar_usuarios()` retorna os históricos completos por padrão. A variante `listar_usuarios(incluir_historico=False)` é usada nas listagens curtas, dispensando a consulta adicional à tabela de trocas.
- A identificação por nome também utiliza uma listagem resumida e busca o histórico **somente** do usuário selecionado.
- A importação opcional de JSON verifica a presença de cadastros sem carregar todas as linhas e seus históricos.
- A opção de exportar JSON está no menu principal do terminal, na pasta `exportacoes/`. Ela apenas consulta o banco.

## Tratamento de erros

- Erros de validação de usuário e pontos são tratados como `ValueError` e exibidos de forma compreensível.
- Falhas na persistência recebem `ErroBanco`, preservando a exceção original como causa (`raise ... from ...`). Erros de programação típicos, como `TypeError` e `AttributeError`, não são ocultados sob uma mensagem genérica de banco.
- O terminal encerra normalmente caso o usuário pressione `Ctrl+C` ou feche a entrada durante menus e pausas, fechando a conexão Oracle no bloco `finally`.

## Testes por responsabilidade

| Arquivo | Escopo |
|---|---|
| `test_cli_basico.py` | Entrada, menus e regras básicas |
| `test_banco_configuracao.py` | Conexão, parâmetros e SQL |
| `test_crud_oracle.py` | Cadastro, alteração, consulta e exclusão |
| `test_pontos_passagens.py` | Créditos, resgates, limites e rollback |
| `test_exportacao_json.py` | Arquivos JSON e integridade |
| `test_api_clima.py` | Open-Meteo, validação e cache |
| `test_api_http.py` | Rotas HTTP e painel local |
| `test_area_pessoal.py` | Identificação e rotas pessoais |
| `test_estrutura.py` | Caminhos, scripts e pontos de entrada |
| `test_refinamento_backend.py` | Regras compartilhadas, consultas enxutas e falhas |

## Atualização do repositório existente

Para evitar conflitos com arquivos antigos, **prefira extrair o ZIP completo em uma pasta nova** e copiar seu `.env` e `.git` com cuidado. Se preferir aplicar apenas a atualização, use o pacote incremental e siga `INSTRUCOES_ATUALIZACAO.txt` para remover os caminhos antigos que foram movidos.

Depois execute `python -m unittest discover -s tests -v`, `python -m scripts.validar_web_oracle` e `python -m scripts.validar_area_pessoal_oracle` no seu Windows, antes de realizar o commit.
