from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.enums import TaskStatus
from app.models.task import Task


def create_task(db: Session, project_id: int, title: str, description: str | None, assignee_id: int | None, created_by_id: int) -> Task:
    task = Task (
        project_id=project_id,
        title=title,
        description=description,
        assignee_id=assignee_id,
        created_by_id=created_by_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks_for_project(db: Session, project_id: int, status: TaskStatus | None) -> list[Task]:
    query = select(Task).options(joinedload(Task.assignee)).where(Task.project_id == project_id).order_by(Task.created_at)
    if status is not None:
        query = query.where(Task.status == status)
    return db.scalars(query).all()