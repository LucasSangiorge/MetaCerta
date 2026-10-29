from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FrankfurterRate(BaseModel):
    date: date
    base: str
    quote: str
    rate: Decimal


class ExchangeRateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    base: str
    quote: str
    rate: Decimal
    rate_date: date
    fetched_at: datetime
