# 💰 MetaCerta

> Plataforma de planejamento de metas financeiras baseada em cotações de moedas, histórico de aportes e projeções personalizadas.

## 📌 Sobre o projeto

O **MetaCerta** é um projeto Backend desenvolvido para simular uma plataforma de planejamento financeiro.

A aplicação permite que o usuário mantenha uma conta com histórico de depósitos, defina metas financeiras em diferentes moedas e acompanhe uma projeção de quanto tempo poderá levar para alcançar seus objetivos.

Para realizar as análises, o sistema consome dados de uma API externa de cotações de moedas e utiliza um pipeline de dados organizado em **Bronze, Silver e Gold**.

### Exemplo

Um usuário deseja alcançar:

> **US$ 5.000**

E informa que consegue guardar:

> **R$ 1.500 por mês**

O sistema utiliza a cotação atual da moeda, o saldo e o histórico de aportes para calcular uma projeção do objetivo.

---

## 🎯 Objetivos de aprendizado

O projeto foi criado com foco no aprendizado prático de:

* Desenvolvimento Backend com Python;
* FastAPI;
* PostgreSQL;
* SQLAlchemy;
* Alembic;
* Autenticação com JWT;
* Consumo de APIs externas;
* Tratamento e validação de dados;
* ETL;
* Arquitetura Bronze, Silver e Gold;
* Regras de negócio;
* Testes automatizados;
* Docker;
* Git e GitHub;
* Documentação de APIs.

---

## 🏗️ Arquitetura

O projeto será dividido em duas principais áreas:

### Backend transacional

Responsável pelas operações da aplicação:

```text
Users
   ↓
Accounts
   ↓
Deposits
   ↓
Goals
   ↓
Reports
```

### Pipeline de dados

Responsável pelo processamento das informações externas:

```text
API de Câmbio
      ↓
   Bronze
      ↓
   Silver
      ↓
    Gold
      ↓
  Análises
```

---

## 📂 Estrutura do projeto

```text
MetaCerta/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   └── modules/
│   │       ├── users/        # model, schema, repository, service, router
│   │       ├── accounts/
│   │       ├── deposits/
│   │       ├── goals/
│   │       └── reports/
│   │
│   └── data/
│       ├── pipelines/        # extract, transform, load, pipeline
│       ├── bronze/
│       ├── silver/
│       └── gold/
│
├── alembic/                  # (Sprint 1)
├── tests/
├── frontend/
├── docs/
├── docker-compose.yaml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧩 Principais módulos

### Users

Gerenciamento dos usuários e autenticação.

### Accounts

Representação das contas financeiras simuladas.

### Deposits

Registro dos aportes realizados pelo usuário.

### Goals

Criação e acompanhamento das metas financeiras.

### Reports

Geração das informações e análises apresentadas ao usuário.

### ETL

Responsável pela extração, transformação e carregamento dos dados de cotações.

---

## 💱 Consumo de API externa

O MetaCerta consumirá uma API externa para obter cotações de moedas.

Inicialmente serão trabalhadas:

* BRL — Real Brasileiro
* USD — Dólar Americano
* EUR — Euro

Fluxo:

```text
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
Pipeline de dados
```

---

## 🥉🥈🥇 Pipeline de dados

### Bronze

Armazena os dados recebidos da fonte externa de forma próxima ao formato original.

### Silver

Responsável pela limpeza, padronização e validação dos dados.

### Gold

Contém dados preparados para análises, projeções e relatórios.

```text
       API
        │
        ▼
     Bronze
        │
        ▼
     Silver
        │
        ▼
      Gold
        │
        ▼
    Análises
```

---

## 🎯 Exemplo de meta

```text
Objetivo: US$ 5.000

Aporte mensal: R$ 1.500

Saldo atual: R$ 7.500

Cotação utilizada: R$ X,XX

Valor da meta em BRL: R$ XX.XXX

Valor já acumulado: US$ X.XXX

Valor restante: US$ X.XXX

Projeção: XX meses
```

> As projeções são estimativas baseadas nos dados e premissas utilizadas pelo sistema. O projeto não oferece recomendação de investimentos.

---

## 🛠️ Tecnologias

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Alembic
* PostgreSQL

### Dados

* Python
* ETL
* Pandas
* Bronze / Silver / Gold

### Infraestrutura

* Docker
* Docker Compose
* GitHub Actions

### Testes

* Pytest

---

## 🚧 Status do projeto

**Em desenvolvimento.**

### Roadmap

* [ ] Sprint 1 — Fundação
* [ ] Sprint 2 — Usuários e autenticação
* [ ] Sprint 3 — Contas e depósitos
* [ ] Sprint 4 — Consumo da API de câmbio
* [ ] Sprint 5 — Pipeline Bronze/Silver/Gold
* [ ] Sprint 6 — Metas e projeções
* [ ] Sprint 7 — Relatórios, testes e deploy

---

## 📚 Objetivo do projeto

Este projeto faz parte do meu processo de desenvolvimento de conhecimentos em **Backend Python, integração de sistemas e engenharia de dados**, buscando aplicar conceitos de desenvolvimento de software em um problema de negócio realista.

---

## 👨‍💻 Autor

**Lucas Sangiorge**

Projeto desenvolvido para fins de estudo, prática e portfólio.
