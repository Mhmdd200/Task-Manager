from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enums import TaskStatus
from app.models.task import Task
from app.models.user import User
from app.repositories import project_repository, task_repository
from app.schemas.task import TaskCreate


def _assignee_not_member() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Assignee must be a member of the project",
    )


def create_task(db: Session, data: TaskCreate, current_user: User, project_id: int) -> Task:
    # the dependency already made sure current_user is a member of the project,
    # so only the assignee needs checking, and only when one was sent
    if data.assignee_id is not None:
        # a user that doesn't exist isn't a member either, so this one check covers both
        if project_repository.get_member(db, project_id, data.assignee_id) is None:
            raise _assignee_not_member()

    return task_repository.create_task(
        db=db,
        project_id=project_id,
        title=data.title,
        description=data.description,
        assignee_id=data.assignee_id,
        created_by_id=current_user.id
    )

def get_tasks(db: Session, project_id: int, status: TaskStatus | None) -> list[Task]:
    return task_repository.get_tasks_for_project(db, project_id, status)
