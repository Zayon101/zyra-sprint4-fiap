# Zyra — Sprint 4 | Etapa 1

Continuação do Zyra (Sprint 3) para a Sprint 4 de Computational Thinking Using Python, FIAP 2026.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Executar

Requer **Python 3.10 ou superior** (o código utiliza `match/case`). Não há dependências externas nesta etapa.

No terminal, dentro da pasta do projeto:

```bash
python main.py
```

No Windows, se o comando `python` não estiver configurado:

```powershell
py main.py
```

## Estrutura

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Ponto de entrada, inicialização e fluxo principal |
| `menus.py` | Telas de menu e navegação |
| `usuarios.py` | Cadastro, consulta, alteração e exclusão |
| `operacoes.py` | Pontos, passagens, histórico e resumo |
| `persistencia.py` | Leitura e gravação JSON (temporária) |
| `constantes.py` | Regras e configurações fixas |
| `utils.py` | Funções de apoio e validação |
| `programa_sprint3_original.py` | Arquivo original, preservado como referência; **não executar esta versão para os testes da Sprint 4** |
| `tests/` | Testes automatizados |

## Estado atual e próximos passos

Esta entrega **não inclui ainda banco SQL nem consumo de API externa**. Nesta Etapa 1, a lógica de execução da Sprint 3 foi mantida, apenas dividida em módulos para facilitar a migração. Até a Etapa 4, o arquivo `dados_zyra.json` continua sendo usado como armazenamento e será criado automaticamente na pasta do projeto.

Na próxima etapa, serão definidas as tabelas e a conexão do banco. Depois disso, o armazenamento JSON será substituído por SQL; a opção de exportação JSON será implementada separadamente.

## Executar testes

```bash
python -m unittest discover -s tests -v
```

## Observações

- As regras atuais foram preservadas (500 pontos iniciais e 587 pontos por passagem unitária).
- O arquivo `dados_zyra.json`, se já existir, pode ser copiado para esta pasta; faça backup antes.
- Não envie dados reais ou senhas de banco no ZIP final.
- O código foi reestruturado com assistência de IA; é necessário documentar os prompts e analisar as decisões no relatório da Sprint 4.
