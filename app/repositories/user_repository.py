from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def get_by_email(db: Session, email: str) -> User | None:
    # this is the query. it is not excuted yet
    query = select(User).where(User.email == email)
    # use scalar to return only one value
    return db.scalar(query)

def create(db: Session, *, name: str, email: str, hashed_password: str) -> User:
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user