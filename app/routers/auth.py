from fastapi import APIRouter, status
from app.dependencies.database import DbSession
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, Token
from app.services import auth_service
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: UserCreate, db: DbSession):
    return auth_service.register_user(db, data)

@router.post(
    "/login",
    response_model=Token
)
def login(data: LoginRequest, db: DbSession):
    user = auth_service.authenticate_user(db, data.email, data.password)
    access_token = auth_service.create_access_token(user.id)
    return Token(access_token=access_token)