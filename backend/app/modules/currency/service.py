import httpx
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.currency import repository
from app.modules.currency.model import ExchangeRate
from app.modules.currency.schema import FrankfurterRate


class ExchangeRateUnavailableError(Exception):
    pass


def get_latest_rate(base: str, quote: str) -> FrankfurterRate:
    try:
        response = httpx.get(
            f"{settings.EXCHANGE_API_URL}/rates",
            params={"base": base, "quotes": quote},
            timeout=settings.EXCHANGE_API_TIMEOUT,
        )
        response.raise_for_status()
        rates = TypeAdapter(list[FrankfurterRate]).validate_json(response.content)
    except (httpx.HTTPError, ValidationError) as error:
        raise ExchangeRateUnavailableError(
            f"Não foi possível obter a cotação de {base}/{quote}: {error}"
        ) from error

    if not rates:
        raise ExchangeRateUnavailableError(
            f"Nenhuma cotação encontrada para {base}/{quote}."
        )

    return rates[0]


def fetch_and_store(db: Session, base: str, quote: str) -> ExchangeRate:
    external = get_latest_rate(base, quote)
    existing = repository.get_by_pair_and_date(db, base, quote, external.date)
    if existing is not None:
        return existing

    rate = ExchangeRate(
        base=base,
        quote=quote,
        rate=external.rate,
        rate_date=external.date,
    )
    repository.add(db, rate)
    db.commit()
    db.refresh(rate)
    return rate
