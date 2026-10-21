from fastapi import APIRouter, HTTPException, status

from app.core.database import SessionDep
from app.modules.accounts import service
from app.modules.accounts.schema import AccountCreate, AccountResponse
from app.modules.auth.dependencies import CurrentUser

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(data: AccountCreate, db: SessionDep, current_user: CurrentUser):
    return service.create_account(db, current_user, data)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: SessionDep, current_user: CurrentUser):
    try:
        return service.get_account(db, current_user, account_id)
    except service.AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada.",
            )from None

