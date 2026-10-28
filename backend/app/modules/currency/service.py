import httpx
from pydantic import TypeAdapter, ValidationError

from app.core.config import settings
from app.modules.currency.schema import ExchangeRate


class ExchangeRateUnavailableError(Exception):
    pass


def get_latest_rate(base: str, quote: str) -> ExchangeRate:
    try:
        response = httpx.get(
            f"{settings.EXCHANGE_API_URL}/rates",
            params={"base": base, "quotes": quote},
            timeout=settings.EXCHANGE_API_TIMEOUT,
        )
        response.raise_for_status()
        rates = TypeAdapter(list[ExchangeRate]).validate_json(response.content)
    except (httpx.HTTPError, ValidationError) as error:    # 4. os dois tipos de erro: o do httpx e o do Pydantic
        raise ExchangeRateUnavailableError(
            f"Não foi possível obter a cotação de {base}/{quote}: {error}"
        ) from error   # 5. uma mensagem que ajude a investigar

    if not rates:
        raise ExchangeRateUnavailableError(
            f"Nenhuma cotação encontrada para {base}/{quote}."
        )

    return rates[0]              


