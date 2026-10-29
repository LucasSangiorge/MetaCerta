from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Identity, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint(
            "base",
            "quote",
            "rate_date",
            name="uq_exchange_rates_base_quote_rate_date",
        ),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    base: Mapped[str] = mapped_column(String(3))
    quote: Mapped[str] = mapped_column(String(3))
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    rate_date: Mapped[date] = mapped_column(Date)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
