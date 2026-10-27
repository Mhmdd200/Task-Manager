from fastapi import APIRouter
from app.dependencies.auth import CurrentUser
from app.dependencies.database import DbSession
from app.schemas.user import UserResponse
from app.services import auth_service, user_service
router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserResponse])
def users(current_user: CurrentUser, db: DbSession):
    return user_service.get_all_users(db)