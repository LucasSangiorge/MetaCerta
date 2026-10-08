🗺️ Roadmap — MetaCerta
Sprint 1 — Fundação do projeto

Objetivo: deixar a base pronta.

 Criar repositório
 Configurar ambiente Python
 FastAPI
 PostgreSQL
 SQLAlchemy
 Alembic
 Docker Compose
 .env / .env.example
 Estrutura por domínio
 Endpoint /health
 README inicial

Resultado:

GET /health

{
    "status": "ok"
}
Sprint 2 — Usuários e autenticação

Objetivo: permitir que o usuário tenha uma conta no sistema.

 Model User
 Cadastro
 Hash de senha
 Login
 JWT
 Usuário autenticado
 Proteção das rotas

Endpoints:

POST /users
POST /auth/login
GET  /users/me
Sprint 3 — Contas e depósitos

Objetivo: criar o histórico financeiro simulado.

 Model Account
 Model Deposit
 Criar conta
 Consultar saldo
 Registrar depósito
 Histórico de depósitos
 Validação de valores
 Relacionamento User → Account → Deposits

Exemplo:

POST /accounts
POST /deposits
GET  /accounts/{id}
GET  /accounts/{id}/deposits
Sprint 4 — Consumo da API de câmbio 🌎

Objetivo: aprender a consumir uma API externa de verdade.

MetaCerta
   ↓
Currency Service
   ↓
API externa
   ↓
JSON
   ↓
Validação
   ↓
Sistema
 Escolher API de câmbio
 Criar CurrencyService
 Fazer requisição HTTP
 Validar resposta
 Tratamento de erros
 Timeout
 Registrar cotações
 USD / EUR / BRL

Esse sprint é especialmente importante para você porque vai te ensinar a diferença entre uma API que você controla e uma API externa da qual seu sistema depende.

Sprint 5 — Bronze → Silver → Gold 🥉🥈🥇

Objetivo: construir nosso pipeline de dados.

API externa
    ↓
BRONZE
    ↓
SILVER
    ↓
GOLD
Bronze

Guardar os dados originais.

Silver

Limpar e padronizar:

datas;
moedas;
valores;
duplicidades;
registros inválidos.
Gold

Criar dados preparados para análise:

histórico cambial;
evolução da cotação;
dados para projeção;
dados das metas.
 Extract
 Transform
 Load
 Bronze
 Silver
 Gold
 Logs da ETL
 Tratamento de falhas
Sprint 6 — Metas e projeções 🎯

Objetivo: transformar os dados em algo útil para o usuário.

O usuário informa:

Meta: US$ 5.000
Aporte mensal: R$ 1.500

O sistema calcula:

Câmbio atual
        ↓
Valor equivalente em BRL
        ↓
Saldo atual
        ↓
Valor restante
        ↓
Projeção

Criar:

Goal
GoalService
ProjectionService

Endpoints:

POST /goals
GET  /goals
GET  /goals/{id}
GET  /goals/{id}/projection

Também podemos testar cenários:

R$ 1.000/mês → X meses
R$ 1.500/mês → X meses
R$ 2.000/mês → X meses
Sprint 7 — Relatórios, testes e produção 🚀

Objetivo: transformar o projeto em portfólio.

 Dashboard/relatório
 Progresso da meta
 Histórico
 Projeções
 Testes unitários
 Testes de integração
 Testes das regras de negócio
 GitHub Actions
 Docker
 Documentação Swagger
 README completo
 Deploy

No final:

Usuário
   ↓
Conta
   ↓
Depósitos
   ↓
Meta
   ↓
Câmbio real
   ↓
ETL
   ↓
Análise
   ↓
Projeção
   ↓
Relatório