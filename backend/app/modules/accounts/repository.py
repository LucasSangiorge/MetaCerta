from sqlalchemy.orm import Session

from app.modules.accounts.model import Account


def get_by_id(db: Session, account_id:int) -> Account | None:
    return db.get(Account, account_id)


def add(db: Session, account:Account) -> Account:
    db.add(account)
    db.flush()
    return account
