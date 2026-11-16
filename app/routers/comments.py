from fastapi import APIRouter, status

from app.dependencies.auth import CurrentUser
from app.dependencies.database import DbSession
from app.dependencies.permissions import TaskAsMember
from app.schemas.comment import CommentCreate, CommentResponse
from app.services import comment_service

# own router: comments only need task_id, so there's no /projects prefix here
router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(data: CommentCreate, task: TaskAsMember, current_user: CurrentUser, db: DbSession):
    # TaskAsMember reads {task_id}: 404 unless the task exists and the caller is a member
    return comment_service.create_comment(db, data, current_user.id, task.id)
