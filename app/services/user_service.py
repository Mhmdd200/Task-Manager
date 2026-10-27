from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories import user_repository

def get_all_users(db: Session) -> list[User]:
    return user_repository.get_all_users(db)