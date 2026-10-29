from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.currency.model import ExchangeRate


def get_by_pair_and_date(
    db: Session,
    base: str,
    quote: str,
    rate_date: date,
) -> ExchangeRate | None:
    return db.scalar(
        select(ExchangeRate).where(
            ExchangeRate.base == base,
            ExchangeRate.quote == quote,
            ExchangeRate.rate_date == rate_date,
        )
    )


def add(db: Session, rate: ExchangeRate) -> ExchangeRate:
    db.add(rate)
    db.flush()
    return rate


def get_latest(
    db: Session,
    base: str,
    quote: str,
) -> ExchangeRate | None:
    return db.scalar(
        select(ExchangeRate)
        .where(ExchangeRate.base == base, ExchangeRate.quote == quote)
        .order_by(ExchangeRate.rate_date.desc())
    )
