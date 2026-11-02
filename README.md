# Zyra — Sprint 4 | Etapa 6: integração com Open-Meteo

Esta versão **substitui a API Trilhos/ARTESP pela API meteorológica pública Open-Meteo**, sem cadastro, CPF, senha ou chave de API. As funcionalidades de Oracle da FIAP, CRUD, pontos, passagens, histórico e exportação JSON das etapas 1–5 foram preservadas.

## Integrantes

- Carolina Kotz Rodrigues — RM 571876 — 1TDSPH
- Felipe Motitsuki Tan — RM 570770 — 1TDSPH
- Gabriel Feitosa de Lima — RM 573026 — 1TDSPH
- João Gabriel Dantas Moura — RM 573101 — 1TDSPH
- Záyon Alves Marques — RM 571205 — 1TDSPH

## Objetivo e relação com o Zyra

O Zyra converte pontos SoulUp em passagens. O recurso **Condições para sua viagem** ajuda a pessoa a planejar deslocamentos em São Paulo, consultando condições meteorológicas e previsão de chuva. Isso é **informação complementar sobre mobilidade**, não informa o funcionamento real das linhas de metrô e não interfere em saldo ou resgates.

### API usada

- Documentação oficial: https://open-meteo.com/en/docs
- Endpoint público: `GET https://api.open-meteo.com/v1/forecast`
- Coordenadas de referência: centro de São Paulo (`latitude=-23.5505`, `longitude=-46.6333`)
- Fuso: `America/Sao_Paulo`
- Condições atuais (`current`): temperatura, sensação térmica, umidade, precipitação, vento e código meteorológico WMO.
- Previsão (`daily`): máximas, mínimas, chance máxima de chuva, precipitação total estimada e condição prevista para três dias.
- Formato de resposta: **JSON**.
- **Não exige API Key** para acesso público não comercial, respeitadas as condições de uso do provedor.
- A API oferece dados meteorológicos previstos/modelados: não equivalem a observações de uma estação física nem a status do transporte.

## Instalação e configuração

1. Extraia o projeto ou aplique apenas os arquivos da atualização na pasta do projeto atual.
2. Preserve o arquivo `.env` **já configurado para o Oracle da FIAP**. Não compartilhe esse arquivo ou o inclua na entrega. Caso ainda não exista, copie `.env.example` para `.env` e configure as variáveis Oracle.
3. **Não precisa configurar nenhuma variável da Open-Meteo**. Se houver uma `ARTESP_API_KEY` antiga no seu `.env`, ela pode ser removida; não é mais utilizada.
4. No terminal do projeto, execute:

   ```powershell
   python -m pip install -r requirements.txt
   python -m unittest discover -s tests -v
   python validar_api_clima.py
   python main.py
   ```

5. No menu principal do Zyra, escolha **[6] Condições para sua viagem (clima)**:
   - **[1]** condições atuais na região central de São Paulo;
   - **[2]** previsão meteorológica para os próximos três dias;
   - **[3]** atualizar manualmente os dados quando passaram pelo menos cinco minutos desde a consulta anterior;
   - **[0]** voltar ao menu principal.

O módulo mantém os dados em cache durante a execução; consultar outra opção do menu não faz nova requisição. A opção de atualização somente faz outra consulta após o intervalo mínimo. Reiniciar o programa reinicia o cache.

## Arquivos envolvidos na substituição

| Arquivo | Responsabilidade |
| --- | --- |
| `api_clima.py` | Requisição HTTP, tratamento de erros, normalização JSON, tradução WMO, cache |
| `clima.py` | Submenu, exibição de condições atuais e previsão |
| `validar_api_clima.py` | Teste da API real, independente do Oracle |
| `main.py` | Conecta a opção 6 ao módulo de clima |
| `menus.py` | Altera o texto da opção 6 |
| `.env.example` | Remove variável de chave ARTESP |
| `tests/test_etapa6.py` | Novos testes da integração Open-Meteo |
| `README.md` | Instruções revisadas |

**Arquivos removidos da versão anterior:** `api_trilhos.py`, `estacoes.py` e `validar_api_metro.py` (e eventual `api_estacoes.py` da Overpass). Esses arquivos não são necessários na nova versão.

**Arquivos não alterados pela migração:** `banco.py`, `repositorio.py`, `usuarios.py`, `operacoes.py`, `criar_tabelas.sql`, `exportacao.py` e as regras de pontuação. **Não recrie as tabelas Oracle.**

## Testes e tratamento de erros

- Os testes automatizados não dependem de rede, de credenciais ou do banco real.
- Os cenários cobrem resposta válida, JSON incompleto, campos inconsistentes, falta de dados, códigos WMO, timeout, erro HTTP, falha de rede, cache, navegação nos menus e ausência de alterações no Oracle.
- **85 testes locais aprovados** após a substituição, abrangendo também a regressão das etapas anteriores.
- A conexão HTTP direta não pôde ser verificada neste ambiente; execute `python validar_api_clima.py` no Windows e confirme a mensagem `[OK]`. Se houver falha, envie o texto do terminal sem credenciais.
- Se a Open-Meteo falhar, o Zyra exibe o erro e permite retornar ao menu. O banco não é modificado pela consulta meteorológica.
- O arquivo JSON `dados_zyra.json` da Sprint 3 não é mais a base principal dos usuários; os registros continuam no Oracle.

## Como explicar na Sprint 4

O código faz um `GET` com a biblioteca `requests`, passando latitude, longitude, indicadores e fuso como parâmetros. A Open-Meteo responde em JSON; o programa valida tipos e campos, interpreta códigos WMO e apresenta valores no terminal. O uso do cache evita consultas repetidas e `try`/`except` trata falhas de rede e respostas inválidas. Explique que os dados de clima são **relevantes para o planejamento do deslocamento**, em complemento à emissão de passagens. O enunciado também permite a alternativa de integração bidirecional com o front-end, que **ainda não foi implementada** nesta etapa.

A documentação/vídeo da entrega deve incluir os prompts de IA efetivamente utilizados, avaliação crítica das sugestões, alterações realizadas pela equipe e relação com o conteúdo estudado.

## Referências

- Open-Meteo Weather Forecast API: https://open-meteo.com/en/docs
- Open-Meteo (repositório e condições de acesso público não comercial): https://github.com/open-meteo/open-meteo
