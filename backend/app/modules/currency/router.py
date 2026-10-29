from fastapi import APIRouter, HTTPException, status

from app.core.database import SessionDep
from app.modules.currency import service
from app.modules.currency.schema import ExchangeRateResponse


router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get("/rates", response_model=list[ExchangeRateResponse])
def list_rate(db: SessionDep):
    try:
        usd = service.fetch_and_store(db, "USD", "BRL")
        eur = service.fetch_and_store(db, "EUR", "BRL")
    except service.ExchangeRateUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cotação indisponível no momento. Tente novamente mais tarde.",
        ) from None
    return [usd, eur]
