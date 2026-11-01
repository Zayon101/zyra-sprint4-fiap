# Zyra — Sprint 4 | Etapa 4: pontos, passagens e histórico

Continuação da Etapa 3, que já teve o CRUD confirmado no **Oracle Database da FIAP**. Agora foram revisadas e reforçadas as regras de negócio de pontos, resgates de passagens e histórico, preservando os menus da Sprint 3 e a persistência Oracle.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Atualizações da Etapa 4

- Adicionado `regras.py`, contendo validação independente do banco/terminal para nomes, pontos, créditos e tipos de passagem.
- Reforçados os limites de dados para corresponder às colunas `NOME VARCHAR2(120 CHAR)` e `PONTOS NUMBER(12)` existentes no Oracle.
- Créditos de pontos utilizam um `UPDATE` **atômico** que impede ultrapassar a capacidade da coluna, inclusive com alterações concorrentes.
- Resgates já operavam com **UPDATE condicionado ao saldo + INSERT do histórico na mesma transação**; o comportamento foi preservado e ampliado com novos testes.
- Consultas ao histórico retornam **ID e data da troca**, usando a coluna `DATA_TROCA` que já existia na Etapa 2. O terminal apresenta essas informações.
- Resumo de valores resgatados utiliza `Decimal` na soma para evitar acumular imprecisões típicas de `float`.
- A aplicação agora apresenta mensagens amigáveis para erros de validação de negócio, sem encerrar o programa.
- Adicionado teste de integração real específico para pontos e resgates (`validar_operacoes_oracle.py`) e testes automatizados de regressão.

### Regras atuais

| Ação | Regra |
| --- | --- |
| Novo cadastro | recebe 500 pontos |
| Créditos | aceita inteiro positivo e soma no Oracle |
| Ajuste manual de saldo | aceita inteiro de 0 a 999.999.999.999 |
| Passagem unitária | 1 viagem, 587 pontos, R$ 5,40 |
| Ida e volta | 2 viagens, 1.174 pontos, R$ 10,80 |
| Pacote de 5 | 5 viagens, 2.935 pontos, R$ 27,00 |
| Saldo insuficiente | bloqueia o resgate, sem gerar histórico |
| Falha ao registrar troca | rollback do desconto de pontos |
| Histórico | cada resgate registra tipo, viagens, custo, valor, ID e data |

> Os valores de passagem continuam sendo **regras fixas da simulação acadêmica**; não representam necessariamente a tarifa oficial vigente.

## Instalação e teste no Windows

**1.** Extraia o ZIP da Etapa 4 em uma pasta própria. Não apague a pasta da Etapa 3.

**2.** Copie somente seu arquivo `.env` local preenchido da Etapa 3 para a pasta da Etapa 4. Não envie esse arquivo para o GitHub.

**3.** No terminal, dentro da pasta nova, execute:

```powershell
py -m pip install -r requirements.txt
py testar_banco.py
```

Os dois objetos `ZYRA_USUARIOS` e `ZYRA_TROCAS` devem aparecer com `[OK]`.

**4.** Execute os testes automatizados (simulações locais de Oracle e regressões):

```powershell
py -m unittest discover -s tests -v
```

**5.** Faça o teste guiado no Oracle real da FIAP:

```powershell
py validar_operacoes_oracle.py
```

Digite `TESTAR` apenas quando quiser autorizar um **cadastro temporário próprio**. O teste atribui 500 pontos, credita mais 100, resgata uma passagem de 587 pontos (saldo 13), confere ID/data/histórico, rejeita um segundo resgate por falta de saldo e verifica a persistência em uma segunda conexão. Ao final, tenta excluir **somente** o cadastro temporário. Se houver erro de limpeza, o script mostra o ID para conferência.

**6.** Execute o sistema:

```powershell
py main.py
```

Você pode cadastrar um usuário de teste no menu 1, adicionar 100 pontos no menu 2, trocar por uma passagem unitária e consultar o histórico no menu 3. Esse usuário de teste manual **não é excluído automaticamente**.

### Não é necessário recriar as tabelas

Esta etapa utiliza a estrutura já criada no Oracle da FIAP. **Não rode `preparar_banco.py` nem `criar_tabelas.sql` novamente.** As colunas de data e os relacionamentos já estavam previstos desde a Etapa 2. O sistema não usa o JSON como fonte principal de dados.

## Principais arquivos modificados/adicionados

| Arquivo | Responsabilidade |
| --- | --- |
| `regras.py` | Regras e validações independentes |
| `repositorio.py` | SQL parametrizado, transações, limites e leitura de histórico com data |
| `operacoes.py` | Exibição do histórico e resumo monetário |
| `utils.py` | Validação de nome e formatação de data |
| `constantes.py` | Limites compatíveis com o esquema Oracle |
| `main.py` | Tratamento amigável de valores fora das regras |
| `validar_operacoes_oracle.py` | Teste guiado no Oracle da FIAP |
| `tests/test_etapa4.py` | Testes de pontos, passagens, histórico, erros e rollback |

Arquivos não alterados (como o SQL de criação, `banco.py` e o CRUD) foram mantidos para não provocar regressões.

## Limitações e cuidados

- Os testes locais usam SQLite para simular consultas e transações, **não um Oracle real**. O teste de integração real precisa ser executado no computador com acesso ao banco da FIAP.
- A opção de alteração manual de saldo substitui o valor atual; o programa não tem auditoria separada de créditos/ajustes, apenas **histórico de resgates**. Caso o projeto exija extrato de movimentações, será necessário criar uma tabela específica numa evolução futura.
- Excluir um usuário exclui também suas trocas pelo `ON DELETE CASCADE` definido no Oracle. Não teste exclusões sobre cadastros reais.
- A coluna `PONTOS NUMBER(12)` limita saldos a 12 dígitos e foi adotada a validação de aplicação correspondente.
- Os dados da Sprint 3 em JSON continuam disponíveis apenas para importação opcional (`importar_json.py`). A exportação de consultas SQL para JSON será desenvolvida na **Etapa 5**.
- Consulte o enunciado da FIAP para registrar no documento e no vídeo os prompts utilizados, as revisões feitas e como o grupo entendeu e testou a solução.

## Próximo passo

**Etapa 5:** implementar opção de consulta e exportação de usuários/histórico para arquivo JSON, a partir do Oracle, sem substituir a persistência do banco.
