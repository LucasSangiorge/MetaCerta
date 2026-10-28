from fastapi import APIRouter, HTTPException, status

from app.core.database import SessionDep
from app.modules.accounts.service import AccountNotFoundError
from app.modules.auth.dependencies import CurrentUser
from app.modules.deposits import service
from app.modules.deposits.schema import DepositCreate, DepositResponse


router = APIRouter(tags=["Deposits"])


@router.post(
    "/deposits", response_model=DepositResponse, status_code=status.HTTP_201_CREATED
)
def create_deposit(data: DepositCreate, db: SessionDep, current_user: CurrentUser):
    try:
        return service.create_deposit(db, current_user, data)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada.",
        ) from None


@router.get("/accounts/{account_id}/deposits", response_model=list[DepositResponse])
def list_deposits(account_id: int, db: SessionDep, current_user: CurrentUser):
    try:
        return service.list_deposits(db, current_user, account_id)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada."
        ) from None
