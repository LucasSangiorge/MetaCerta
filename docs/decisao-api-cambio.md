# Decisão: API de câmbio

- **Status:** aceita
- **Data:** 2026-10-28
- **Issue:** #13

## Contexto

O MetaCerta precisa de cotações de moedas para duas finalidades:

1. **Cotação atual** de USD e EUR em relação ao BRL, para converter o valor das metas (Sprint 6).
2. **Histórico de cotações por período**, para o pipeline de dados Bronze → Silver → Gold (Sprint 5).

Como as metas são projetadas em **meses**, uma cotação por dia é suficiente. Não é necessário valor em tempo real.

Critérios avaliados: precisa de chave de acesso, cobre USD/EUR/BRL, oferece histórico por período, facilidade de uso do JSON e confiabilidade da fonte.

## Opções avaliadas

Todas foram chamadas de verdade em 2026-10-28 e responderam sem chave de acesso.

| Critério | AwesomeAPI | Frankfurter (v2) | PTAX (Banco Central do Brasil) |
|---|---|---|---|
| Chave de acesso | não exigiu no teste | não exige | não exige |
| USD, EUR e BRL | sim | sim | sim, mas o EUR fica em outro endpoint |
| Cotação atual | tempo real (compra, venda, máxima, mínima) | uma por dia | uma por dia útil |
| Histórico por período | parcial ("últimos N dias") | sim, com `from` e `to` | sim |
| Formato do JSON | simples; valores como texto | o mais simples: uma lista de registros `{date, base, quote, rate}` | OData, mais verboso; datas em mês-dia-ano |
| Fonte | serviço privado brasileiro | bancos centrais e fontes oficiais; código aberto | fonte oficial brasileira |

## Decisão

Usar a **Frankfurter, versão 2** (`https://api.frankfurter.dev/v2/rates`) como fonte principal.

Exemplos testados:

```text
GET https://api.frankfurter.dev/v2/rates?base=USD&quotes=BRL,EUR
GET https://api.frankfurter.dev/v2/rates?base=USD&quotes=BRL&from=2026-10-20&to=2026-10-27
```

Resposta (cada item é uma cotação):

```json
[
  {"date": "2026-10-28", "base": "USD", "quote": "BRL", "rate": 5.3506},
  {"date": "2026-10-28", "base": "USD", "quote": "EUR", "rate": 0.89653}
]
```

## Por quê

- **O histórico por período sai numa chamada só**, com `from` e `to`, o que atende direto o pipeline da Sprint 5.
- **O formato em lista de registros** já corresponde a linhas de tabela, então a camada Bronze guarda a resposta quase sem transformação.
- **Não exige chave de acesso**, o que simplifica a configuração e não adiciona um segredo ao `.env`.
- **É código aberto e pode ser hospedada pelo próprio projeto**, o que reduz a dependência de um serviço de terceiros.

## Consequências

- **Uma cotação por dia.** Suficiente para metas em meses; o MetaCerta não mostra variação ao longo do dia.
- **Os valores vêm como número no JSON** (`5.3506`). Na conversão para `Decimal`, não usar `Decimal(float)`, que carrega a imprecisão do float. Converter a partir do texto (`Decimal(str(valor))`) ou deixar o Pydantic validar o campo como `Decimal`.
- **Usar o endereço novo.** O endereço antigo (`api.frankfurter.app`) responde com redirecionamento permanente (301) para `api.frankfurter.dev`. O cliente HTTP deve apontar direto para o novo.
- **A API externa pode falhar.** O serviço de câmbio (issue #14) precisa de timeout e de tratamento de erro, sem derrubar a API do MetaCerta.
- **Alternativa de reserva:** se a Frankfurter ficar indisponível, a AwesomeAPI é a opção mais próxima (tempo real, sem chave no teste). A PTAX fica como referência oficial, caso o projeto precise dela no futuro.

## Pendências

- Os limites de uso (requisições por minuto) não foram encontrados na documentação pública da Frankfurter. Rever se o volume de chamadas crescer.
