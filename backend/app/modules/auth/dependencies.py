from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status

from app.core.database import SessionDep
from app.core.security import decode_access_token, oauth2_scheme
from app.modules.users import repository as users_repository
from app.modules.users.model import User

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possivel validar as credenciais",
    headers={"WW-Authenticate": "Bearer"},
)

def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: SessionDep,
) -> User:
    try:
        user_id = int(decode_access_token(token))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_exception from None

    user = users_repository.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user

CurrentUser= Annotated[User, Depends(get_current_user)]
