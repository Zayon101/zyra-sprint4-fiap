# Zyra — Sprint 4 | Etapa 5: exportação JSON das consultas Oracle

Esta versão **continua a Etapa 4**, validada no Oracle Database da FIAP. Mantém CRUD, pontos, resgates e histórico e adiciona exportação de consultas SQL para arquivos JSON, sem substituir a persistência no banco.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Funcionalidades adicionadas

Na tela principal, foi incluída a opção **[5] Exportar consultas em JSON**, com um submenu:

| Opção | Consulta realizada | Conteúdo do JSON |
| --- | --- | --- |
| 1 — Todos os usuários | SELECT de usuários e histórico | Lista de cadastros com saldos e resgates |
| 2 — Usuário por ID | SELECT parametrizado por ID | Cadastro e histórico de um usuário |
| 3 — Histórico por usuário | SELECT parametrizado por ID | Resgates, com ID, data, pontos e valor |
| 4 — Resumo geral | SELECT de usuários e trocas | Totais de usuários, pontos, trocas, viagens e valores |
| 0 — Voltar | — | Retorna ao menu anterior |

As consultas reutilizam as funções existentes em `RepositorioOracle` (`repositorio.py`) e **não executam INSERT, UPDATE, DELETE nem COMMIT**.

A tela de resumo e o arquivo JSON agora compartilham a função `calcular_resumo()` do módulo `relatorios.py` para evitar divergências de cálculo.

## Como instalar e executar no Windows

1. Extraia o ZIP em uma pasta nova, mantendo uma cópia da Etapa 4.
2. Copie **somente** o arquivo `.env` da sua Etapa 4 para a pasta desta etapa. Não altere suas tabelas Oracle.
3. Dentro da pasta do projeto, execute:

```powershell
py -m pip install -r requirements.txt
py testar_banco.py
py -m unittest discover -s tests -v
py main.py
```

O banco deve exibir `[OK]` para `ZYRA_USUARIOS` e `ZYRA_TROCAS`. No menu principal, pressione **5** para abrir as exportações. Ao terminar, o programa informa o caminho completo do arquivo criado.

### Onde ficam os arquivos?

São gravados na pasta **`exportacoes/`**, criada automaticamente ao lado de `main.py`.

Exemplos de nomes gerados:

- `zyra_usuarios_20261101_103000_123456.json`
- `zyra_usuario_4_20261101_103001_123456.json`
- `zyra_historico_4_20261101_103002_123456.json`
- `zyra_resumo_20261101_103003_123456.json`

O timestamp torna os nomes únicos na prática, e o modo de criação exclusiva (`x`) impede sobrescrever um arquivo já existente mesmo em caso de colisão. O arquivo usa UTF-8, indentação de 4 espaços e acentos preservados. Datas de trocas são exportadas em texto ISO 8601, como `2026-11-01T10:30:00`.

Quando não existe nenhum usuário, a exportação geral gera uma lista vazia válida. Para consultas por ID inexistente, **nenhum arquivo é criado**.

> **Privacidade:** os arquivos JSON podem incluir nomes, IDs e históricos dos cadastros. A pasta `exportacoes/` está no `.gitignore`. Evite compartilhar exportações com dados reais sem revisar o conteúdo.

## Como validar com o Oracle real da FIAP

Depois de executar o `testar_banco.py`, rode:

```powershell
py validar_exportacao_oracle.py
```

Esse teste automatizado **não modifica o banco de dados**. Faz consultas reais, exporta para uma pasta temporária, confere os JSONs e **remove os arquivos temporários** ao final. Verifica:

1. Todos os usuários e sua quantidade.
2. O resumo geral e os totais.
3. Um cadastro por ID e o histórico desse cadastro, **se houver ao menos um usuário**.

Se não houver usuários no banco, o teste informa que os dois casos por ID não puderam ser exercitados. Nesse caso, cadastre um usuário de teste no `main.py` e execute novamente, se desejar validar todos os cenários. O script de validação não cria nem exclui usuários.

O programa principal, por outro lado, **mantém** os JSONs exportados na pasta `exportacoes/`, para serem utilizados na entrega acadêmica.

## Principais arquivos adicionados ou modificados

| Arquivo | Papel |
| --- | --- |
| `exportacao.py` | Montagem dos dados, serialização JSON e escrita segura |
| `relatorios.py` | Cálculo único dos indicadores da tela e do JSON |
| `menus.py` | Novo submenu de exportação |
| `main.py` | Nova opção `[5]` do menu principal |
| `operacoes.py` | Reutilização dos cálculos de `relatorios.py` |
| `validar_exportacao_oracle.py` | Validação com consultas Oracle reais e arquivos temporários |
| `tests/test_etapa5.py` | Testes automatizados dos quatro tipos de exportação |
| `.gitignore` | Exclusão dos JSONs exportados do controle de versão |

Os demais módulos da Etapa 4 foram preservados, incluindo SQL, conexão Oracle, operações de resgate e validações.

## Limitações e próximos passos

- Os testes automatizados de unidade e integração simulada usam SQLite; o teste `validar_exportacao_oracle.py` verifica a exportação em **Oracle real** somente no seu ambiente da FIAP.
- Os valores de passagem seguem as regras didáticas do Zyra e não equivalem necessariamente às tarifas oficiais atuais.
- Exportação JSON é **cópia dos resultados consultados**, não um mecanismo de sincronização bidirecional com o Oracle. As alterações de usuários e pontos continuam ocorrendo exclusivamente no banco.
- Não é necessário executar novamente `preparar_banco.py` ou `criar_tabelas.sql`.
- Para a entrega da Sprint 4, registrem os prompts de IA usados e uma análise crítica das sugestões, das modificações e das verificações feitas pela equipe, como pede o enunciado.

**Próxima etapa:** integração com uma API externa pública relevante para o Zyra (consulta de estações de metrô).
