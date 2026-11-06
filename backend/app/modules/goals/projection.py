from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal


CENTS = Decimal("0.01")


@dataclass(frozen=True)
class Projection:
    target_in_account_currency: Decimal
    accumulated_in_target_currency: Decimal
    remaining_in_account_currency: Decimal
    remaining_in_target_currency: Decimal
    months_remaining: int
    progress_percent: Decimal
    goal_reached: bool


def money(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def calculate_projection(
    target_amount: Decimal,
    exchange_rate: Decimal,
    current_balance: Decimal,
    monthly_contribution: Decimal,
) -> Projection:
    """Calcula quantos meses faltam para atingir a meta.

    exchange_rate converte 1 unidade da moeda da meta para a moeda da conta
    (ex.: meta em USD, conta em BRL, cotação 5.40). Função pura: não acessa
    banco nem API, para poder ser testada com valores feitos à mão.
    """
    if exchange_rate <= 0:
        raise ValueError("A cotação precisa ser maior que zero.")
    if monthly_contribution <= 0:
        raise ValueError("O aporte mensal precisa ser maior que zero.")

    target = money(target_amount * exchange_rate)
    remaining = max(target - current_balance, Decimal("0"))

    if remaining == 0:
        months = 0
    else:
        months = int(
            (remaining / monthly_contribution).to_integral_value(rounding=ROUND_CEILING)
        )

    progress = min(current_balance / target * 100, Decimal("100"))

    return Projection(
        target_in_account_currency=target,
        accumulated_in_target_currency=money(current_balance / exchange_rate),
        remaining_in_account_currency=money(remaining),
        remaining_in_target_currency=money(remaining / exchange_rate),
        months_remaining=months,
        progress_percent=money(progress),
        goal_reached=remaining == 0,
    )
