from decimal import Decimal

import pytest


def test_deposito_atualiza_o_saldo(client, auth, account):
    for amount in ["100.50", "200.25", "50"]:
        response = client.post(
            "/deposits",
            json={"account_id": account["id"], "amount": amount},
            headers=auth,
        )
        assert response.status_code == 201

    balance = client.get(f"/accounts/{account['id']}", headers=auth).json()["balance"]
    deposits = client.get(f"/accounts/{account['id']}/deposits", headers=auth).json()

    assert Decimal(balance) == Decimal("350.75")
    # O saldo sempre bate com a soma do histórico de depósitos
    assert sum(Decimal(d["amount"]) for d in deposits) == Decimal(balance)


def test_deposito_na_conta_de_outro_usuario_responde_404(
    client, auth, account, create_user
):
    other = create_user("bruno@example.com")

    response = client.post(
        "/deposits", json={"account_id": account["id"], "amount": "100"}, headers=other
    )

    assert response.status_code == 404
    balance = client.get(f"/accounts/{account['id']}", headers=auth).json()["balance"]
    assert Decimal(balance) == Decimal("0")


def test_deposito_com_valor_zero_responde_422(client, auth, account):
    response = client.post(
        "/deposits", json={"account_id": account["id"], "amount": "0"}, headers=auth
    )

    assert response.status_code == 422


def test_deposito_que_falha_nao_altera_o_saldo(client, db, auth, account, monkeypatch):
    """Atomicidade: o depósito já foi inserido e o saldo já foi alterado na
    sessão, mas o commit falha. Nada pode sobrar: nem o depósito, nem o saldo."""
    client.post(
        "/deposits", json={"account_id": account["id"], "amount": "100"}, headers=auth
    )

    def fail() -> None:
        raise RuntimeError("falha simulada no commit")

    monkeypatch.setattr(db, "commit", fail)
    with pytest.raises(RuntimeError):
        client.post(
            "/deposits",
            json={"account_id": account["id"], "amount": "999"},
            headers=auth,
        )
    monkeypatch.delattr(db, "commit")

    balance = client.get(f"/accounts/{account['id']}", headers=auth).json()["balance"]
    deposits = client.get(f"/accounts/{account['id']}/deposits", headers=auth).json()
    assert Decimal(balance) == Decimal("100")
    assert len(deposits) == 1
