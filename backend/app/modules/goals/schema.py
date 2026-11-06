from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GoalCreate(BaseModel):
    account_id: int
    name: str = Field(min_length=3, max_length=100)
    target_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    target_currency: str = Field(min_length=3, max_length=3)
    monthly_contribution: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @field_validator("target_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("A moeda deve ter 3 letras, por exemplo USD.")
        return value.upper()


class GoalProjectionResponse(BaseModel):
    goal_id: int
    name: str
    target_amount: Decimal
    target_currency: str
    account_currency: str
    exchange_rate: Decimal
    rate_date: date
    target_in_account_currency: Decimal
    current_balance: Decimal
    accumulated_in_target_currency: Decimal
    remaining_in_account_currency: Decimal
    remaining_in_target_currency: Decimal
    monthly_contribution: Decimal
    months_remaining: int
    progress_percent: Decimal
    goal_reached: bool


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    name: str
    target_amount: Decimal
    target_currency: str
    monthly_contribution: Decimal
    created_at: datetime
