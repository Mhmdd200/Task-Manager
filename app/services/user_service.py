from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories import user_repository

def _user_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

def get_user_or_404(db: Session, user_id: int) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise _user_not_found()
    return user

def get_all_users(db: Session) -> list[User]:
    return user_repository.get_all_users(db)