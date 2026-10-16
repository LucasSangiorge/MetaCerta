from fastapi import APIRouter, HTTPException, status

from app.core.database import SessionDep
from app.modules.auth.dependencies import CurrentUser
from app.modules.users import service
from app.modules.users.schema import UserCreate, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: SessionDep):
    try:
        return service.create_user(db, data)
    except service.EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado.",
        ) from None

@router.get("/me", response_model= UserResponse)
def read_me(current_user: CurrentUser):
    return current_user
