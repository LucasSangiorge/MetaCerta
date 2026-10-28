from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.deposits.model import Deposit


def add(db: Session, deposit: Deposit) -> Deposit:
    db.add(deposit)
    db.flush()
    return deposit


def list_by_account(db: Session, account_id: int) -> list[Deposit]:
    query = (
        select(Deposit)
        .where(Deposit.account_id == account_id)
        .order_by(Deposit.created_at.desc())
    )

    return list(db.scalars(query).all())
