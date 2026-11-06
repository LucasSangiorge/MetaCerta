from sqlalchemy.orm import Session

from app.modules.accounts import service as accounts_service
from app.modules.goals import repository
from app.modules.goals.model import Goal
from app.modules.goals.schema import GoalCreate
from app.modules.users.model import User


class GoalNotFoundError(Exception):
    pass


def create_goal(db: Session, user: User, data: GoalCreate) -> Goal:
    accounts_service.get_account(db, user, data.account_id)

    goal = Goal(
        account_id=data.account_id,
        name=data.name,
        target_amount=data.target_amount,
        target_currency=data.target_currency,
        monthly_contribution=data.monthly_contribution,
    )

    repository.add(db, goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_goal(db: Session, user: User, goal_id: int) -> Goal:
    goal = repository.get_by_id(db, goal_id)

    if goal is None or goal.account.user_id != user.id:
        raise GoalNotFoundError(goal_id)

    return goal


def list_goals(db: Session, user: User) -> list[Goal]:
    return repository.list_by_user(db, user.id)
