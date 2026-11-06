from fastapi import APIRouter, HTTPException, status

from app.core.database import SessionDep
from app.modules.accounts.service import AccountNotFoundError
from app.modules.auth.dependencies import CurrentUser
from app.modules.goals import service
from app.modules.goals.schema import GoalCreate, GoalResponse


router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(data: GoalCreate, db: SessionDep, current_user: CurrentUser):
    try:
        return service.create_goal(db, current_user, data)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada.",
        ) from None


@router.get("", response_model=list[GoalResponse])
def list_goals(db: SessionDep, current_user: CurrentUser):
    return service.list_goals(db, current_user)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: int, db: SessionDep, current_user: CurrentUser):
    try:
        return service.get_goal(db, current_user, goal_id)
    except service.GoalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta não encontrada.",
        ) from None
