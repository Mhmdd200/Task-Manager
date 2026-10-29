from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings

password_hash = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def register_user(db: Session, data: UserCreate) -> User:
    email = data.email.lower()
    if user_repository.get_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    return user_repository.create(
        db,
        name=data.name,
        email=email, 
        hashed_password=hash_password(data.password)
    )
    
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email.lower())
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
