from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.accounts.model import Account
from app.modules.goals.model import Goal


def get_by_id(db: Session, goal_id: int) -> Goal | None:
    return db.get(Goal, goal_id)


def add(db: Session, goal: Goal) -> Goal:
    db.add(goal)
    db.flush()
    return goal


def list_by_user(db: Session, user_id: int) -> list[Goal]:
    query = (
        select(Goal)
        .join(Goal.account)
        .where(Account.user_id == user_id)
        .order_by(Goal.created_at)
    )

    return list(db.scalars(query).all())
