# Zyra — Sprint 4 | Etapa 7: integração com o front-end web

O Zyra converte pontos SoulUp em passagens simuladas de metrô. Nesta versão, o **Oracle da FIAP** é a fonte de dados única dos menus Python e de uma API HTTP local que pode ser consumida pelo front-end. O painel web de demonstração já está incluído; a integração com as páginas React existentes ainda depende de receber o código desse projeto.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Funcionalidades preservadas

- CRUD Oracle de usuários, com bônus de 500 pontos no cadastro.
- Crédito de pontos, resgate de passagens, histórico, resumo e regras de saldo.
- Exportação de consultas SQL para arquivos JSON, sob demanda.
- Consulta de clima e previsão para São Paulo via **Open-Meteo** (`https://open-meteo.com/en/docs`), sem chave para uso não comercial.
- Menus do terminal em `main.py`, sem alterações na navegação.

## Preparação

1. Mantenha seu arquivo `.env` com as credenciais Oracle válidas da FIAP. Nunca inclua esse arquivo no ZIP da entrega nem no repositório Git.
2. Instale as dependências atuais:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Confirme o banco existente com `python testar_banco.py`. **Não execute `preparar_banco.py` novamente** se as tabelas já existirem.
4. Execute `python main.py` para continuar usando o terminal; execute `python validar_api_clima.py` para testar a Open-Meteo.

---

## Etapa 7 — Integração com o front-end web

Esta etapa acrescenta uma **API HTTP local** que acessa o **mesmo Oracle da FIAP** utilizado pelos menus do terminal. As operações web não usam arquivo JSON como banco de dados; utilizam o `RepositorioOracle`, preservando o CRUD e as regras de pontos/resgates. Não foi necessário alterar as tabelas SQL.

### Rodar e demonstrar a integração

1. Preserve seu `.env` preenchido com as configurações do Oracle.
2. No terminal da pasta do projeto, execute `python testar_banco.py`.
3. Execute `python servidor_web.py` (mantenha esse terminal aberto).
4. Abra **http://127.0.0.1:8765/** no navegador.
5. Cadastre um usuário de demonstração no painel e consulte-o também em `python main.py` (use outro terminal). Altere o nome, credite pontos e resgate uma passagem no site; observe no terminal. Faça também uma alteração no terminal e clique em **Atualizar dados** no site para comprovar o sentido inverso.
6. Para encerrar o servidor, use `Ctrl+C`.

Para um teste automatizado contra o Oracle real, execute `python validar_web_oracle.py` e digite `TESTAR`. Ele cria um usuário temporário, verifica as operações via HTTP em outra conexão Oracle e tenta excluí-lo ao final. **Ele escreve apenas nesse usuário temporário**; não execute em uma base de produção ou compartilhada sem autorização.

Os testes locais não necessitam de credenciais nem de acesso à internet:

```powershell
python -m unittest discover -s tests -v
```

### Endpoints da API HTTP local

| Método | Rota | Operação |
| --- | --- | --- |
| GET | `/api/status` | Verifica servidor local |
| GET | `/api/usuarios` | Lista usuários e históricos |
| POST | `/api/usuarios` | Cadastra `{ "nome": "Ana Maria" }` |
| GET | `/api/usuarios/1` | Consulta cadastro pelo ID |
| PATCH | `/api/usuarios/1` | Altera `{ "nome": "Ana Paula" }` ou `{ "pontos": 600 }` |
| DELETE | `/api/usuarios/1` | Exclui usuário e seus resgates |
| POST | `/api/usuarios/1/pontos` | Credita `{ "quantidade": 100 }` |
| POST | `/api/usuarios/1/resgates` | Resgata `{ "tipo": 1 }` (1–3) |
| GET | `/api/resumo` | Indicadores do banco Oracle |
| GET | `/api/passagens` | Tipos de passagem e seus custos |
| GET | `/api/clima` | Clima e previsão via Open-Meteo |

Requisições de escrita devem enviar `Content-Type: application/json` e `X-Zyra-Cliente: painel-web`. A API retorna erros JSON com códigos HTTP (400, 404, 409, 502, 503 etc.). Para utilizar uma origem Vite no desenvolvimento, o servidor aceita `http://localhost:5173` e `http://127.0.0.1:5173` com CORS controlado. O exemplo de cliente TypeScript está em `integracao_react/zyraApi.ts`.

### Escopo e segurança

- `painel_web/` é **um painel independente de demonstração**, não uma alteração direta no código do front-end Zyra React/Vite, que não foi fornecido nesta etapa. Para integrar as telas oficiais do React será necessário adaptar seu código e testar a integração nele. **Não declare que esse passo já foi feito** na apresentação.
- O servidor usa exclusivamente `127.0.0.1:8765` e **não possui autenticação**; foi criado apenas para testes acadêmicos locais. Não o exponha à rede, à internet, a túneis públicos ou a uma hospedagem sem autenticação, autorização, TLS e controles adicionais.
- O painel acessa **dados reais do Oracle**. Evite usar cadastros pessoais reais nas demonstrações, pois nomes/saldos ficam disponíveis localmente. Use usuários fictícios.
- O terminal (`main.py`) permanece funcionando como antes. Servidor e terminal utilizam **conexões independentes**, com alterações confirmadas em transações. O painel reflete mudanças feitas no terminal após clicar em Atualizar dados; não há atualização em tempo real por WebSocket.
- Não houve nova dependência no `requirements.txt`; o servidor usa a biblioteca padrão `http.server` do Python.

### Evidências para o vídeo da Sprint 4

Mostre, nessa ordem, um cadastro no navegador, a consulta do mesmo usuário no terminal, um crédito/resgate no terminal e a atualização dos dados no navegador. Explique: `fetch` HTTP → `servidor_web.py` → `servico_web.py` → `RepositorioOracle` → Oracle. Demonstre também um erro 409 para saldo insuficiente e a consulta de clima pela Open-Meteo. Apresente os prompts reais usados com IA e sua análise crítica conforme exigência do professor.
