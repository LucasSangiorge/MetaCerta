# 💰 MetaCerta

> API de planejamento de metas financeiras em moeda estrangeira: quanto falta e em quantos meses você chega lá, com a cotação do dia.

O usuário mantém uma conta com histórico de depósitos, cria uma meta em outra moeda (por exemplo, **US$ 5.000** para uma viagem) e informa quanto consegue guardar por mês. A API busca a cotação atual, converte a meta para a moeda da conta, desconta o saldo e calcula **quantos meses faltam**.

Em paralelo, um **pipeline de dados Bronze → Silver → Gold** coleta o histórico de cotações e gera tabelas prontas para análise.

---

## 🎯 Exemplo de projeção

```text
Meta:            US$ 5.000
Aporte mensal:   R$ 1.500
Saldo da conta:  R$ 7.500
Cotação usada:   R$ 5,40   (ilustrativa: a API usa a cotação do dia)

Meta em BRL:     5.000 × 5,40        = R$ 27.000,00
Falta:           27.000 − 7.500      = R$ 19.500,00  (US$ 3.611,11)
Projeção:        19.500 ÷ 1.500      = 13 meses
Progresso:       27,78%
```

`GET /goals/{id}/projection` devolve exatamente esses valores (há um teste automatizado para esse exemplo).

> As projeções são estimativas com base na cotação do dia e no aporte informado. O projeto não oferece recomendação de investimentos.

---

## 🔌 Endpoints

| Método | Rota | O que faz |
|---|---|---|
| `POST` | `/users` | Cadastro (senha com hash Argon2) |
| `POST` | `/auth/login` | Login, devolve um token JWT |
| `GET` | `/users/me` | Usuário autenticado |
| `POST` | `/accounts` | Cria uma conta (ex.: BRL) |
| `GET` | `/accounts` · `/accounts/{id}` | Lista e consulta contas, com saldo |
| `POST` | `/deposits` | Registra um depósito e atualiza o saldo na **mesma transação** |
| `GET` | `/accounts/{id}/deposits` | Histórico de depósitos |
| `POST` | `/goals` | Cria uma meta ligada a uma conta |
| `GET` | `/goals` · `/goals/{id}` | Lista e consulta metas |
| `GET` | `/goals/{id}/projection` | **Projeção**: cotação, valor em BRL, acumulado, restante e meses |
| `GET` | `/currency/rates` | Cotações atuais USD/BRL e EUR/BRL |
| `GET` | `/health` | Saúde da API e do banco |

Todas as rotas de contas, depósitos e metas exigem token. Recurso de outro usuário responde **404**, sem revelar que ele existe.

A documentação interativa (Swagger) fica em `http://127.0.0.1:8000/docs`.

---

## 🧠 Decisões técnicas

- **Dinheiro em `Decimal`, nunca `float`.** No banco, `NUMERIC(12, 2)`; nos cálculos, `Decimal` com arredondamento explícito. Valores estatísticos do pipeline (médias, variação %) podem ser float, arredondados.
- **Regras também no banco.** `CHECK (amount > 0)` em depósitos e `CHECK (target_amount > 0)` / `CHECK (monthly_contribution > 0)` em metas: mesmo que alguém pule a validação da API, o PostgreSQL recusa.
- **Depósito atômico.** O insert do depósito e a atualização do saldo acontecem em um único commit; se algo falha no meio, nada fica gravado (coberto por teste).
- **Meta ligada à conta, não ao usuário.** A projeção precisa de um saldo, e quem tem saldo é a conta. O dono é conferido por `account.user_id`.
- **Cálculo da projeção isolado** em uma função pura (`goals/projection.py`), sem banco nem FastAPI, testada com valores feitos à mão.
- **Falha da API de câmbio tratada.** Timeout, erro HTTP e JSON inválido viram um erro de domínio. Se a API estiver fora, a projeção usa a última cotação gravada; sem nenhuma, responde **503**.
- **Alembic desde o primeiro dia**, com convenção de nomes para constraints (`pk_`, `fk_`, `ix_`, `ck_`, `uq_`).
- **Organização por domínio**: cada módulo tem `model`, `schema`, `repository`, `service` e `router`.

---

## 🥉🥈🥇 Pipeline de dados

```text
API Frankfurter ──► Bronze ──► Silver ──► Gold
                   (bruto)   (limpo)   (analítico)
```

| Camada | O que faz | Formato |
|---|---|---|
| **Bronze** (`extract.py`) | Baixa 365 dias de cotações USD/BRL e EUR/BRL, sem alterar nada | JSON |
| **Silver** (`transform.py`) | Padroniza tipos, mantém a cotação em decimal exato e remove duplicados por par + data | Parquet |
| **Gold** (`load.py`) | Tabela **diária** (variação % e média móvel de 30 dias) e **mensal** (média, mínima, máxima, fechamento) | Parquet |

O `pipeline.py` roda as três etapas em sequência, com log e tempo de cada uma. Se uma etapa falha, as seguintes não rodam e o processo sai com código 1 (útil para agendadores e CI).

A escolha da API de câmbio está documentada em [docs/decisao-api-cambio.md](docs/decisao-api-cambio.md).

---

## 🧪 Testes

```bash
pytest
```

**44 testes**, rodando em banco SQLite em memória e com a API de câmbio simulada: não acessam o banco de produção nem a internet.

- **Unitários:** cálculo da projeção (exemplo do README, arredondamento, meta atingida) e validações de valores e moedas.
- **Integração:** cadastro/login/JWT, depósitos (saldo = soma do histórico, atomicidade), metas (isolamento entre usuários, projeção, fallback de cotação e 503) e o cliente da API de câmbio (timeout, erro 500, JSON inválido).

---

## ▶️ Como rodar

Pré-requisitos: Python 3.12+ e Docker (para o PostgreSQL local) ou um banco no [Neon](https://neon.tech).

```bash
# 1. Ambiente
python -m venv .venv
source .venv/Scripts/activate        # Windows (Git Bash); no Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 2. Variáveis de ambiente
cp .env.example .env                 # preencha DATABASE_URL e SECRET_KEY

# 3. Banco
docker compose up -d                 # PostgreSQL + pgAdmin (opcional se usar o Neon)
alembic upgrade head                 # cria as tabelas

# 4. API (a partir da pasta backend)
cd backend
uvicorn app.main:app --reload        # http://127.0.0.1:8000/docs

# 5. Pipeline de dados (também a partir de backend)
python -m data.pipelines.pipeline

# 6. Testes (a partir da raiz)
cd .. && pytest
```

---

## 🛠️ Tecnologias

- **Backend:** Python, FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, PostgreSQL (Neon), JWT, Argon2, httpx
- **Dados:** pandas, PyArrow, Parquet, arquitetura Bronze/Silver/Gold
- **Testes:** pytest, TestClient
- **Infra local:** Docker Compose (PostgreSQL + pgAdmin)

---

## 📂 Estrutura

```text
MetaCerta/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/            # config, database, security
│   │   └── modules/
│   │       ├── users/       # model, schema, repository, service, router
│   │       ├── auth/
│   │       ├── accounts/
│   │       ├── deposits/
│   │       ├── currency/    # cliente da API de câmbio
│   │       └── goals/       # metas + projection.py
│   └── data/
│       └── pipelines/       # config, extract, transform, load, pipeline
├── alembic/                 # migrations
├── tests/                   # 44 testes
├── docs/
├── docker-compose.yaml
├── pyproject.toml
└── requirements.txt
```

---

## 🚦 Status

**Concluído.** O projeto foi organizado em sprints, com uma issue e um pull request por tarefa.

| Sprint | Entrega |
|---|---|
| 1 — Fundação | FastAPI, configuração, PostgreSQL, Alembic, `/health` |
| 2 — Usuários | Cadastro com hash, login JWT, rotas protegidas |
| 3 — Contas e depósitos | Contas, depósitos atômicos e histórico |
| 4 — API de câmbio | Cliente httpx com timeout, validação e tratamento de falhas |
| 5 — Pipeline | Bronze, Silver e Gold com orquestração e logs |
| 6 — Metas e projeções | CRUD de metas e projeção de meses |
| 7 — Testes | 44 testes automatizados |

**Fora do escopo desta versão** (ficaram como aprendizado para o próximo projeto, que já começa com eles desde o primeiro dia): Dockerfile da API, CI com GitHub Actions, deploy e orquestração do pipeline com Airflow.

---

## 👨‍💻 Autor

**Lucas Sangiorge** · [GitHub](https://github.com/LucasSangiorge) · [LinkedIn](https://linkedin.com/in/lucas-sangiorge)

Projeto de estudo e portfólio, desenvolvido com apoio de um assistente de IA (Claude Code) como tutor e revisor.
