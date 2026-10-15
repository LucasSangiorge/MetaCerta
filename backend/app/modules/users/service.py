from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.modules.users import repository
from app.modules.users.model import User
from app.modules.users.schema import UserCreate


class EmailAlreadyRegisteredError(Exception):
    pass


def create_user(db: Session, data: UserCreate) -> User:
    if repository.get_by_email(db, data.email) is not None:
        raise EmailAlreadyRegisteredError(data.email)

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    repository.add(db, user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = repository.get_by_email(db, email)

    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user
