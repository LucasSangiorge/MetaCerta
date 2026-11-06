from datetime import date
from decimal import Decimal

import httpx
import pytest

from app.modules.currency import service


# A fixture automática "exchange_api_offline" substitui get_latest_rate;
# aqui testamos a função original, simulando só o httpx (sem internet).
get_latest_rate = service.get_latest_rate


def fake_get(status_code=200, json=None, error=None):
    def _get(url, **kwargs):
        if error is not None:
            raise error
        return httpx.Response(status_code, json=json, request=httpx.Request("GET", url))

    return _get


def test_le_a_cotacao_da_api(monkeypatch):
    payload = [{"date": "2026-11-06", "base": "USD", "quote": "BRL", "rate": 5.4321}]
    monkeypatch.setattr(httpx, "get", fake_get(json=payload))

    rate = get_latest_rate("USD", "BRL")

    assert rate.rate == Decimal("5.4321")
    assert rate.date == date(2026, 11, 6)


@pytest.mark.parametrize(
    "fake",
    [
        fake_get(error=httpx.ConnectTimeout("timeout")),
        fake_get(status_code=500, json={"error": "fora"}),
        fake_get(json=[{"campo": "inesperado"}]),
        fake_get(json=[]),
    ],
    ids=["timeout", "erro-500", "json-invalido", "lista-vazia"],
)
def test_falhas_da_api_viram_erro_de_cotacao_indisponivel(monkeypatch, fake):
    monkeypatch.setattr(httpx, "get", fake)

    with pytest.raises(service.ExchangeRateUnavailableError):
        get_latest_rate("USD", "BRL")
