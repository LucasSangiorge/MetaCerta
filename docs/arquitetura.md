                         ┌─────────────────────┐
                         │    API de Câmbio    │
                         │   USD / EUR / BRL   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       BRONZE        │
                         │    Dados brutos     │
                         └──────────┬──────────┘
                                    │
                                  ETL Pydantic / Pandas
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       SILVER        │
                         │ Dados tratados      │
                         └──────────┬──────────┘
                                    │
                            Regras / análise
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │        GOLD         │
                         │ Dados analíticos    │
                         └──────────┬──────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────┐
│                       BACKEND                             │
│                         FastAPI                           │
│                                                          │
│ Users │ Accounts │ Deposits │ Goals │ Reports │ Currency │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
                     ┌────────────┐
                     │ PostgreSQL │
                     └────────────┘