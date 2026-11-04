from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enums import TaskStatus
from app.models.task import Task
from app.models.user import User
from app.repositories import project_repository, task_repository
from app.schemas.task import TaskCreate, TaskUpdate


def _assignee_not_member() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Assignee must be a member of the project",
    )

def _task_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )


def _cant_update_task() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You can't update this task",
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
    
def update_task(db: Session, task: Task, data: TaskUpdate, current_user: User) -> Task:
    # the dependency already made sure the task is in the project and current_user is a member.
    # permission is checked against the task BEFORE the update: a removed assignee loses access
    project = project_repository.get_by_id(db, task.project_id)
    if current_user.id not in (project.owner_id, task.created_by_id, task.assignee_id):
        raise _cant_update_task()

    # only the fields the client sent (see the comment in project_service.update_project)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return task

    # "assignee_id" missing: keep the assignee, None: unassign, an id: must be a member
    if updates.get("assignee_id") is not None:
        if project_repository.get_member(db, task.project_id, updates["assignee_id"]) is None:
            raise _assignee_not_member()

    return task_repository.update_task(db, task, updates)

def get_tasks(db: Session, project_id: int, status: TaskStatus | None) -> list[Task]:
    return task_repository.get_tasks_for_project(db, project_id, status)

def get_task_or_404(db: Session, task_id: int, project_id: int) -> Task:
    task = task_repository.get_task_by_id_and_project_id(db, task_id, project_id)
    if task is None:
        raise _task_not_found()
    return task
