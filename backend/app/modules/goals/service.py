from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.accounts import service as accounts_service
from app.modules.currency import repository as currency_repository
from app.modules.currency import service as currency_service
from app.modules.goals import repository
from app.modules.goals.model import Goal
from app.modules.goals.projection import calculate_projection
from app.modules.goals.schema import GoalCreate, GoalProjectionResponse
from app.modules.users.model import User


class GoalNotFoundError(Exception):
    pass


def create_goal(db: Session, user: User, data: GoalCreate) -> Goal:
    accounts_service.get_account(db, user, data.account_id)

    goal = Goal(
        account_id=data.account_id,
        name=data.name,
        target_amount=data.target_amount,
        target_currency=data.target_currency,
        monthly_contribution=data.monthly_contribution,
    )

    repository.add(db, goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_goal(db: Session, user: User, goal_id: int) -> Goal:
    goal = repository.get_by_id(db, goal_id)

    if goal is None or goal.account.user_id != user.id:
        raise GoalNotFoundError(goal_id)

    return goal


def list_goals(db: Session, user: User) -> list[Goal]:
    return repository.list_by_user(db, user.id)


def get_exchange_rate(db: Session, base: str, quote: str) -> tuple[Decimal, date]:
    """Cotação mais recente de base -> quote.

    Tenta a API de câmbio (e grava no banco). Se a API estiver fora, usa a
    última cotação já gravada. Sem nenhuma das duas, a projeção não é possível.
    """
    if base == quote:
        return Decimal("1"), date.today()

    try:
        rate = currency_service.fetch_and_store(db, base, quote)
    except currency_service.ExchangeRateUnavailableError:
        rate = currency_repository.get_latest(db, base, quote)
        if rate is None:
            raise

    return rate.rate, rate.rate_date


def get_projection(db: Session, user: User, goal_id: int) -> GoalProjectionResponse:
    goal = get_goal(db, user, goal_id)
    account = goal.account

    exchange_rate, rate_date = get_exchange_rate(
        db, goal.target_currency, account.currency
    )
    projection = calculate_projection(
        target_amount=goal.target_amount,
        exchange_rate=exchange_rate,
        current_balance=account.balance,
        monthly_contribution=goal.monthly_contribution,
    )

    return GoalProjectionResponse(
        goal_id=goal.id,
        name=goal.name,
        target_amount=goal.target_amount,
        target_currency=goal.target_currency,
        account_currency=account.currency,
        exchange_rate=exchange_rate,
        rate_date=rate_date,
        current_balance=account.balance,
        monthly_contribution=goal.monthly_contribution,
        target_in_account_currency=projection.target_in_account_currency,
        accumulated_in_target_currency=projection.accumulated_in_target_currency,
        remaining_in_account_currency=projection.remaining_in_account_currency,
        remaining_in_target_currency=projection.remaining_in_target_currency,
        months_remaining=projection.months_remaining,
        progress_percent=projection.progress_percent,
        goal_reached=projection.goal_reached,
    )
