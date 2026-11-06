from datetime import date
from decimal import Decimal

from app.modules.currency.model import ExchangeRate


def create_goal(client, auth, account_id, **overrides):
    data = {
        "account_id": account_id,
        "name": "Viagem",
        "target_amount": "5000",
        "target_currency": "USD",
        "monthly_contribution": "1500",
        **overrides,
    }
    return client.post("/goals", json=data, headers=auth)


def deposit(client, auth, account_id, amount):
    client.post(
        "/deposits", json={"account_id": account_id, "amount": amount}, headers=auth
    )


def test_cria_lista_e_busca_meta(client, auth, account):
    created = create_goal(client, auth, account["id"])

    assert created.status_code == 201
    goal = created.json()
    assert goal["target_currency"] == "USD"
    assert client.get("/goals", headers=auth).json() == [goal]
    assert client.get(f"/goals/{goal['id']}", headers=auth).json() == goal


def test_usuario_nao_ve_meta_de_outro(client, auth, account, create_user):
    goal = create_goal(client, auth, account["id"]).json()
    other = create_user("bruno@example.com")

    assert client.get("/goals", headers=other).json() == []
    assert client.get(f"/goals/{goal['id']}", headers=other).status_code == 404
    assert (
        client.get(f"/goals/{goal['id']}/projection", headers=other).status_code == 404
    )


def test_nao_cria_meta_na_conta_de_outro(client, account, create_user):
    other = create_user("bruno@example.com")

    response = create_goal(client, other, account["id"])

    assert response.status_code == 404


def test_projecao_do_exemplo_do_readme(client, auth, account, exchange_rate):
    exchange_rate("5.40")
    deposit(client, auth, account["id"], "7500")
    goal = create_goal(client, auth, account["id"]).json()

    response = client.get(f"/goals/{goal['id']}/projection", headers=auth)

    assert response.status_code == 200
    body = response.json()
    assert Decimal(body["exchange_rate"]) == Decimal("5.40")
    assert Decimal(body["target_in_account_currency"]) == Decimal("27000.00")
    assert Decimal(body["current_balance"]) == Decimal("7500.00")
    assert Decimal(body["remaining_in_account_currency"]) == Decimal("19500.00")
    assert body["months_remaining"] == 13
    assert body["goal_reached"] is False


def test_projecao_de_meta_ja_atingida(client, auth, account, exchange_rate):
    exchange_rate("5.00")
    deposit(client, auth, account["id"], "6000")
    goal = create_goal(client, auth, account["id"], target_amount="1000").json()

    body = client.get(f"/goals/{goal['id']}/projection", headers=auth).json()

    assert body["goal_reached"] is True
    assert body["months_remaining"] == 0


def test_meta_na_mesma_moeda_da_conta_nao_consulta_cambio(client, auth, account):
    # A API de câmbio está "fora" (fixture padrão) e mesmo assim funciona
    goal = create_goal(
        client, auth, account["id"], target_currency="BRL", target_amount="3000"
    ).json()

    body = client.get(f"/goals/{goal['id']}/projection", headers=auth).json()

    assert Decimal(body["exchange_rate"]) == Decimal("1")
    assert body["months_remaining"] == 2


def test_api_fora_usa_ultima_cotacao_gravada(client, db, auth, account):
    db.add(
        ExchangeRate(
            base="USD", quote="BRL", rate=Decimal("5.10"), rate_date=date(2026, 11, 5)
        )
    )
    db.commit()
    goal = create_goal(client, auth, account["id"]).json()

    body = client.get(f"/goals/{goal['id']}/projection", headers=auth).json()

    assert Decimal(body["exchange_rate"]) == Decimal("5.10")
    assert body["rate_date"] == "2026-11-05"


def test_api_fora_e_sem_cotacao_gravada_responde_503(client, auth, account):
    goal = create_goal(client, auth, account["id"]).json()

    response = client.get(f"/goals/{goal['id']}/projection", headers=auth)

    assert response.status_code == 503
