# Zyra — Sprint 4 | Etapa 3: CRUD com Oracle

Continuação direta da Etapa 2 validada no Oracle da FIAP. Os menus agora operam sobre as tabelas **`ZYRA_USUARIOS`** e **`ZYRA_TROCAS`**. A antiga persistência JSON foi substituída pelo banco, que passou a ser a **fonte principal dos dados**.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Passo a passo no Windows (VS Code)

**1.** Extraia o ZIP em uma pasta nova. **Não substitua nem apague sua pasta da Etapa 2.**

**2.** Copie o arquivo **`.env` preenchido da Etapa 2** para a pasta da Etapa 3. O ZIP só contém o modelo `.env.example` porque não deve transportar suas credenciais.

**3.** No terminal, dentro da pasta da Etapa 3, instale as dependências (se já instaladas, nada relevante será alterado):

```powershell
py -m pip install -r requirements.txt
```

**4.** Confira que as tabelas já criadas continuam acessíveis:

```powershell
py testar_banco.py
```

As duas tabelas devem aparecer com `[OK]`. **Não execute `preparar_banco.py` novamente se as tabelas já estão criadas.**

**5.** Execute o Zyra conectado ao banco:

```powershell
py main.py
```

Os submenus continuam sendo `Gerenciar usuários`, `Pontos e passagens`, `Histórico de trocas` e `Resumo do sistema`.

## Testar cada operação do CRUD

No menu **1. Gerenciar usuários**:

1. Cadastre um usuário de teste; anote o ID gerado automaticamente pelo Oracle e confirme o bônus de 500 pontos (**CREATE**).
2. Liste todos os usuários e consulte o novo cadastro por ID (**READ**).
3. Altere o nome e o saldo; consulte novamente para confirmar a atualização (**UPDATE**).
4. Exclua o usuário de teste após confirmação; consulte o mesmo ID e verifique que não existe (**DELETE**).
5. Encerre o programa e execute novamente. Os dados deverão refletir diretamente o conteúdo atual do banco.

### Verificação automática opcional no Oracle real

```powershell
py validar_crud_oracle.py
```

O script pede a confirmação `TESTAR`, cria **um usuário temporário próprio**, executa CREATE, READ, UPDATE e DELETE e tenta remover esse cadastro ao final, mesmo que algo falhe. Não executa alterações em outros usuários. Use somente na conta Oracle da equipe e confira eventual alerta de falha de limpeza.

## Regras de pontos e passagens

Para evitar que o sistema mantenha saldos diferentes no JSON e no Oracle, as operações básicas de pontos também passaram a ser gravadas no banco **já nesta etapa**:

- Cadastrar usuário concede bônus de 500 pontos.
- Adicionar pontos atualiza `ZYRA_USUARIOS.PONTOS` sem sobrescrever alterações de outra execução.
- Resgatar uma passagem exige pontos suficientes e registra a operação em `ZYRA_TROCAS`.
- O desconto e o histórico da troca são confirmados **juntos**, na mesma transação; se qualquer operação falhar, ambos são desfeitos.
- Histórico de trocas e resumo consultam o conteúdo atual do banco.

A Etapa 4 poderá aprofundar as regras de negócio, validações, rastreabilidade e casos de teste. A exportação das consultas SQL para JSON ainda será implementada na **Etapa 5**, como consta no roteiro.

## Se você já tem dados antigos da Sprint 3

O programa novo **não lê `dados_zyra.json` automaticamente**. Isso evita divergência entre o arquivo e o banco.

Para importar os usuários e históricos de um JSON anterior:

1. Faça um backup do `dados_zyra.json` antigo e mantenha-o na pasta da Etapa 2 ou em outro local seguro.
2. Copie uma versão desse arquivo para a pasta da Etapa 3.
3. Confira que **não existem usuários cadastrados em `ZYRA_USUARIOS`**. A importação não apaga nem sobrescreve os existentes.
4. Execute:

   ```powershell
   py importar_json.py
   ```

5. O script valida o arquivo e pede para digitar `IMPORTAR`. Todos os usuários e respectivos históricos são importados em uma única transação. Em caso de erro, nenhuma importação parcial é confirmada.
6. **O Oracle gera novos IDs.** O programa mostra o mapeamento do ID antigo para o novo. Não execute a importação novamente.

Se você não tiver cadastros antigos que precise preservar, ignore totalmente esse passo. Se **já houver usuários no Oracle**, não apague nada para forçar a importação: é melhor avaliar uma mesclagem na etapa seguinte.

## Arquivos principais

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Entrada da aplicação, gerenciamento da conexão e mensagens de falha |
| `menus.py` | Navegação pelos menus e submenus |
| `usuarios.py` | Interação no terminal para CREATE, READ, UPDATE e DELETE |
| `repositorio.py` | SQL parametrizado e transações Oracle (CRUD, pontos e trocas) |
| `operacoes.py` | Regras de pontos, passagens e apresentação de histórico/resumo |
| `banco.py` | Configuração do `.env` e conexão Oracle |
| `importar_json.py` | Migração opcional, validada e não destrutiva do JSON anterior |
| `validar_crud_oracle.py` | Teste opt-in do CRUD no Oracle real |
| `constantes.py` | Regras fixas de pontuação e passagens |
| `utils.py` | Validação de entradas e formatação de valores |
| `tests/` | Testes locais e simulações de conexão/SQL |
| `programa_sprint3_original.py` | Cópia preservada da entrega anterior |

O script `criar_tabelas.sql` foi preservado sem modificações porque a estrutura da Etapa 2 já foi criada no banco.

## Testes automatizados locais

```powershell
py -m unittest discover -s tests -v
```

As simulações de CRUD usam **SQLite apenas dentro dos testes**, como substituto controlado para avaliar a lógica SQL e as transações. O projeto principal usa **Oracle exclusivamente**. Esses testes **não comprovam** a execução real na FIAP: execute também `validar_crud_oracle.py` ou faça as operações manualmente no banco real.

## Segurança e limitações

- Nunca compartilhe `.env`, senha, host restrito, backups com dados pessoais nem capturas contendo credenciais.
- Use `INSERT`, `SELECT`, `UPDATE`, `DELETE` com parâmetros vinculados (bind variables), nunca concatenação de entradas do usuário dentro do SQL.
- O banco Oracle gera os IDs de usuários; não se calcula o próximo ID percorrendo listas.
- A tabela `ZYRA_TROCAS` possui uma chave estrangeira com `ON DELETE CASCADE`: excluir um usuário também elimina o histórico dele. Confirme antes de apagar dados reais.
- Não execute `criar_tabelas.sql` nem scripts de reset desnecessariamente.
- A comunicação com o front-end e o consumo de API pública serão tratados em etapas posteriores.
- Registre o uso de IA e as decisões e testes revisados pela equipe no documento e no vídeo, conforme o enunciado.

## Próxima etapa

**Etapa 4:** refinar e validar regras de pontos, passagens, histórico e tratamento de erros no Oracle; em seguida, **Etapa 5:** exportar consultas para JSON.
