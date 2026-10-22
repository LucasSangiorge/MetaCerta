from sqlalchemy.orm import Session

from app.modules.accounts import repository
from app.modules.accounts.schema import AccountCreate
from app.modules.accounts.model import Account
from app.modules.users.model import User

class AccountNotFoundError(Exception):
    pass

def create_account(db: Session, user: User, data: AccountCreate) -> Account:
    account = Account(
        user_id= user.id,
        name= data.name,
        currency= data.currency,
    )

    repository.add(db, account)
    db.commit()
    db.refresh(account)
    return account

def get_account(db: Session, user:User, account_id: int) -> Account:
    account = repository.get_by_id(db, account_id)

    if account is None or account.user_id != user.id:
        raise AccountNotFoundError(account_id)

    return account

def list_accounts(db: Session, user: User) -> list[Account]:
    return repository.list_by_user(db,user.id)

