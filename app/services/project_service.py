from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enums import Role
from app.models.project import Project
from app.models.project_members import ProjectMember
from app.models.user import User
from app.repositories import project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services import user_service


def _project_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Project not found",
    )


def _already_a_member() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User is already a member of this project",
    )


# ---------- permission rules (plain functions: no Depends, no HTTP details) ----------

def get_project_or_404(db: Session, project_id: int) -> Project:
    project = project_repository.get_by_id(db, project_id)
    if project is None:
        raise _project_not_found()
    return project


def get_project_for_member(db: Session, project_id: int, current_user: User) -> Project:
    """Rule 1 + 2: the project must exist AND the user must belong to it."""
    project = get_project_or_404(db, project_id)
    if project_repository.get_member(db, project_id, current_user.id) is None:
        # same error as "does not exist", so strangers can't tell the project exists
        raise _project_not_found()
    return project


def get_project_for_owner(db: Session, project_id: int, current_user: User) -> Project:
    """Rule 1 + 2 + 3: exists, user belongs to it, and user is the owner."""
    project = get_project_for_member(db, project_id, current_user)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can do this",
        )
    return project


# ---------- actions ----------

def get_projects_for_user(db: Session, current_user: User) -> list[Project]:
    return project_repository.get_all_projects_for_user(db, current_user.id)

def create_project(db: Session, data: ProjectCreate, current_user: User) -> Project:
    return project_repository.create(
        db,
        name=data.name,
        description=data.description,
        user_id=current_user.id
    )
    
def update_project(db: Session, project: Project, data: ProjectUpdate) -> Project:
    # only the fields the client actually sent
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return project
    return project_repository.update(db, project, updates)

def delete_project(db: Session, project: Project):
    return project_repository.delete(db, project)

def add_member(db: Session, project: Project, user_id: int) -> ProjectMember:
    # 404 first: there is no point checking membership for a user that doesn't exist
    user_service.get_user_or_404(db, user_id)
    # get_member returns None instead of raising, which is what we need here
    if project_repository.get_member(db, project.id, user_id) is not None:
        raise _already_a_member()
    # role is always "member"; making someone an owner will be a separate action
    return project_repository.add_member(db, project.id, user_id, Role.MEMBER)
