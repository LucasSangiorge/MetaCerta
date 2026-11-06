from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.deposits.schema import DepositCreate
from app.modules.goals.schema import GoalCreate


VALID_GOAL = {
    "account_id": 1,
    "name": "Viagem",
    "target_amount": "5000",
    "target_currency": "USD",
    "monthly_contribution": "1500",
}


def test_moeda_da_meta_vira_maiuscula():
    goal = GoalCreate(**{**VALID_GOAL, "target_currency": "usd"})

    assert goal.target_currency == "USD"


@pytest.mark.parametrize("currency", ["US", "DOLAR", "U$D", "123"])
def test_moeda_invalida_e_recusada(currency):
    with pytest.raises(ValidationError):
        GoalCreate(**{**VALID_GOAL, "target_currency": currency})


@pytest.mark.parametrize("field", ["target_amount", "monthly_contribution"])
@pytest.mark.parametrize("value", ["0", "-10"])
def test_valores_da_meta_precisam_ser_positivos(field, value):
    with pytest.raises(ValidationError):
        GoalCreate(**{**VALID_GOAL, field: value})


def test_meta_com_mais_de_2_casas_decimais_e_recusada():
    with pytest.raises(ValidationError):
        GoalCreate(**{**VALID_GOAL, "target_amount": "10.999"})


@pytest.mark.parametrize("amount", ["0", "-1", "10.001"])
def test_deposito_invalido_e_recusado(amount):
    with pytest.raises(ValidationError):
        DepositCreate(account_id=1, amount=amount)


def test_deposito_valido():
    deposit = DepositCreate(account_id=1, amount="150.50")

    assert deposit.amount == Decimal("150.50")
