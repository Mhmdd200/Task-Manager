from sqlalchemy import func, select, update
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

def delete_task(db: Session, task: Task):
    db.delete(task)
    db.commit()
    
def update_task(db: Session, task: Task, updates: dict) -> Task:
    for field, value in updates.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

def unassign_member_tasks(db: Session, project_id: int, user_id: int) -> None:
    # no commit here: the caller commits this together with removing the member
    query = (
        update(Task)
        .where(Task.project_id == project_id, Task.assignee_id == user_id)
        .values(assignee_id=None)
    )
    db.execute(query)

def get_tasks_for_project(db: Session, project_id: int, status: TaskStatus | None, offset: int, limit: int) -> list[Task]:
    query = select(Task).options(joinedload(Task.assignee)).where(Task.project_id == project_id).order_by(Task.created_at, Task.id)
    if status is not None:
        query = query.where(Task.status == status)
    query = query.offset(offset).limit(limit)
    return db.scalars(query).all()

def get_task_by_id_and_project_id(db: Session, task_id: int, project_id: int) -> Task | None:
    query = select(Task).where(Task.id==task_id, Task.project_id==project_id)
    return db.scalar(query)

def count_tasks_for_project(db: Session, project_id: int, status: TaskStatus | None) -> int:
    query = select(func.count()).select_from(Task).where(Task.project_id == project_id)
    if status is not None:
        query = query.where(Task.status == status)
    return db.scalar(query)