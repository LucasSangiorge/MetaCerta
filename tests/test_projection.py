from decimal import Decimal

import pytest

from app.modules.goals.projection import calculate_projection


def test_exemplo_do_readme():
    # US$ 5.000, cotação 5,40, saldo R$ 7.500, aporte R$ 1.500/mês
    projection = calculate_projection(
        target_amount=Decimal("5000"),
        exchange_rate=Decimal("5.40"),
        current_balance=Decimal("7500"),
        monthly_contribution=Decimal("1500"),
    )

    assert projection.target_in_account_currency == Decimal("27000.00")
    assert projection.remaining_in_account_currency == Decimal("19500.00")
    assert projection.remaining_in_target_currency == Decimal("3611.11")
    assert projection.accumulated_in_target_currency == Decimal("1388.89")
    assert projection.months_remaining == 13
    assert projection.progress_percent == Decimal("27.78")
    assert projection.goal_reached is False


def test_meses_arredondam_para_cima():
    # Faltam R$ 1.501: com R$ 1.500/mês ainda é preciso um 2º mês
    projection = calculate_projection(
        Decimal("1501"), Decimal("1"), Decimal("0"), Decimal("1500")
    )

    assert projection.months_remaining == 2


def test_divisao_exata_nao_soma_mes_extra():
    projection = calculate_projection(
        Decimal("3000"), Decimal("1"), Decimal("0"), Decimal("1500")
    )

    assert projection.months_remaining == 2


def test_meta_ja_atingida():
    projection = calculate_projection(
        Decimal("1000"), Decimal("5.40"), Decimal("6000"), Decimal("1500")
    )

    assert projection.goal_reached is True
    assert projection.months_remaining == 0
    assert projection.remaining_in_account_currency == Decimal("0.00")
    assert projection.progress_percent == Decimal("100.00")


def test_mesma_moeda_usa_cotacao_1():
    projection = calculate_projection(
        Decimal("10000"), Decimal("1"), Decimal("2500"), Decimal("500")
    )

    assert projection.target_in_account_currency == Decimal("10000.00")
    assert projection.months_remaining == 15


@pytest.mark.parametrize(
    ("rate", "contribution"),
    [(Decimal("0"), Decimal("100")), (Decimal("5"), Decimal("0"))],
)
def test_cotacao_ou_aporte_zero_sao_recusados(rate, contribution):
    with pytest.raises(ValueError):
        calculate_projection(Decimal("1000"), rate, Decimal("0"), contribution)
