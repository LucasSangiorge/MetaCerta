# Migrations com Alembic

Guia de como o MetaCerta altera o banco de dados. Toda mudança de estrutura (tabela, coluna, índice, regra) passa por uma migration do Alembic. O projeto **não** usa `Base.metadata.create_all()`.

## Onde rodar os comandos

Sempre na **raiz** do projeto (onde está o `alembic.ini`), com o `.venv` ativado:

```bash
source .venv/Scripts/activate
```

Se aparecer `No 'script_location' key found in configuration`, você está dentro de `backend/`. Volte para a raiz com `cd ..`.

## Comandos do dia a dia

| Comando | O que faz |
|---|---|
| `alembic current` | mostra em qual migration o banco está |
| `alembic history` | lista a corrente de migrations |
| `alembic revision --autogenerate -m "descrição"` | gera uma migration comparando os models com o banco |
| `alembic revision -m "descrição"` | gera uma migration vazia, para escrever à mão |
| `alembic upgrade <rev_atual>:head --sql` | mostra o SQL que será executado, **sem aplicar** |
| `alembic upgrade head` | aplica todas as migrations pendentes |
| `alembic downgrade -1` | desfaz a última migration |
| `alembic check` | confere se os models e o banco estão iguais |

## Fluxo para uma mudança nova

1. Altere ou crie o model em `backend/app/modules/<domínio>/model.py`.
2. Se for um model novo, registre-o em `backend/app/models.py` (é esse arquivo que a API e o Alembic usam para enxergar os models).
3. Gere a migration: `alembic revision --autogenerate -m "descrição"`.
4. **Revise o arquivo gerado** em `alembic/versions/` (veja o checklist abaixo).
5. Confira o SQL: `alembic upgrade <rev_atual>:head --sql`.
6. Aplique: `alembic upgrade head` e confira com `alembic current`.
7. Faça o commit da migration **junto** com o model. A migration faz parte do código.

## Checklist de revisão

Antes de aplicar, confira no arquivo gerado:

- [ ] O `down_revision` aponta para a migration anterior (a corrente está certa).
- [ ] As colunas, os tipos e o `nullable` batem com o model.
- [ ] As chaves estrangeiras apontam para as tabelas certas.
- [ ] A ordem das tabelas respeita as dependências: quem é referenciado é criado **antes**.
- [ ] Os nomes seguem a `NAMING_CONVENTION`: `pk_`, `fk_`, `ix_`, `uq_`, `ck_`.
- [ ] O `downgrade()` desfaz **exatamente** o `upgrade()`, com os mesmos nomes e na ordem inversa.
- [ ] O `upgrade()` não está vazio (`pass`). Se estiver, o model não foi registrado em `app/models.py`.

## Regras

1. **Nunca edite uma migration que já foi aplicada.** Ela é histórico: o Alembic não roda de novo, então a mudança não chega ao banco atual, e ainda quebra a criação de um banco novo. Toda mudança vira uma migration **nova**, no fim da corrente. Para desfazer uma edição acidental: `git restore alembic/versions/<arquivo>.py`.
2. **O model e a migration contam a mesma história.** Uma regra criada na migration também deve existir no model.
3. **Revise sempre o que o `--autogenerate` gerou.** Ele é um ponto de partida, não a palavra final.

## Limites do `--autogenerate`

Ele **não detecta** algumas mudanças. Nesses casos, escreva a migration à mão:

- **`CheckConstraint` em tabela que já existe.**
- **Renomear uma coluna:** ele entende como "apagar uma coluna e criar outra", o que **perde os dados**. Use `op.alter_column(..., new_column_name=...)`.
- **Renomear uma tabela:** use `op.rename_table(...)`.

### Exemplo: migration escrita à mão

A regra de que todo depósito deve ser positivo (`alembic revision -m "check amount positivo em deposits"`):

```python
def upgrade() -> None:
    op.create_check_constraint(
        op.f("ck_deposits_amount_positive"),
        "deposits",
        "amount > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_deposits_amount_positive"),
        "deposits",
        type_="check",
    )
```

O `op.f(...)` diz ao Alembic para usar o nome exatamente como está, sem aplicar a convenção de nomes de novo.

E a mesma regra no model:

```python
class Deposit(Base):
    __tablename__ = "deposits"
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive"),)
```

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| `No 'script_location' key found` | o comando foi rodado dentro de `backend/`, e não na raiz |
| `ModuleNotFoundError: No module named 'app'` | o `prepend_sys_path = backend` saiu do `alembic.ini` |
| A migration gerada vem vazia | o model não foi registrado em `backend/app/models.py` |
| A tabela nova não aparece no painel do Neon | a lista do painel está desatualizada; recarregue a página |
| `alembic check` acusa diferença | um model foi alterado sem gerar a migration correspondente |
