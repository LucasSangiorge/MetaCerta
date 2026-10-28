from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DepositCreate(BaseModel):
    account_id: int
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )


class DepositResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    amount: Decimal
    created_at: datetime
