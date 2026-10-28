from sqlalchemy.orm import Session

from app.modules.accounts import service as accounts_service
from app.modules.accounts.model import Account
from app.modules.deposits import repository
from app.modules.deposits.model import Deposit
from app.modules.deposits.schema import DepositCreate
from app.modules.users.model import User


def create_deposit(db: Session, user: User, data: DepositCreate) -> Deposit:
    account = accounts_service.get_account(db, user, data.account_id)

    deposit = Deposit(
        account_id=data.account_id,
        amount=data.amount,
    )

    repository.add(db, deposit)

    account.balance = Account.balance + data.amount

    db.commit()
    db.refresh(deposit)

    return deposit


def list_deposits(db: Session, user: User, account_id: int) -> list[Deposit]:
    accounts_service.get_account(db, user, account_id)

    return repository.list_by_account(db, account_id)
