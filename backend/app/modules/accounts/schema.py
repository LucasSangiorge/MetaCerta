from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class AccountCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    currency: str = Field(min_length=3, max_length=3)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    currency: str
    balance: Decimal
    created_at: datetime
