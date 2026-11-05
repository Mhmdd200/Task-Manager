from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enums import Role
from app.models.project import Project
from app.models.project_members import ProjectMember
from app.models.user import User
from app.repositories import project_repository, task_repository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services import user_service


def _project_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Project not found",
    )

def _member_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Member not found",
    )

def _already_a_member() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User is already a member of this project",
    )

def _owner_cant_be_deleted() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Owner cannot be deleted",
    )

def _member_cant_be_deleted() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Member cannot be deleted",
    )

def _role_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Role cannot be found",
    )
    
# do this because we can't use the dependencies as they return 404 (here we want T or F)
def is_owner(project_member: ProjectMember):
    return project_member.role == Role.OWNER

def is_member(project_member: ProjectMember):
    return project_member.role == Role.MEMBER
    
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
    # model_dump(exclude_unset=True) keeps only the fields the client SENT, whatever their value:
    #   {"name": "abc"}  -> {"name": "abc"}   sent with a value: kept
    #   {"name": null}   -> {"name": None}    sent as null: KEPT (it is "set", just to None)
    #   {}               -> {}                not sent: excluded
    # it checks "was the key in the request?", not "does it have a value?".
    # (exclude_none=True is the one that drops null values, which would make
    #  "set this to null" impossible, e.g. unassigning a task)
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

def get_members_for_project(db: Session, project_id: int) -> list[ProjectMember]:
    return project_repository.get_members_for_project(db, project_id)

def delete_member_for_project(db: Session, project_id: int, user_id: int, current_user: User):
    # here the user_id is the one to be deleted, and the current user is the user we get from the token
    # we have 2 different flows
    # if he is owner => can remove any
    # if he is member => user_id must be himself
    
    
    # first get the project member for this project_id+user_id
    project_member_to_be_deleted = project_repository.get_member(db, project_id, user_id)
    # second get the project member for the current user
    project_member_for_current_user = project_repository.get_member(db, project_id, current_user.id)
    if not project_member_to_be_deleted:
        raise _member_not_found()
    # here i will validate on the roles explicitly so that in future if there is more roles we handle them
    # if the current user is owner and the user to be deleted is member always delete
    if is_owner(project_member_to_be_deleted):
        raise _owner_cant_be_deleted()
    
    if is_member(project_member_for_current_user):
        if user_id != current_user.id:
            raise _member_cant_be_deleted()
    elif not is_owner(project_member_for_current_user):
        raise _role_not_found()

    # one transaction: the only commit is inside delete_member_from_project,
    # so the unassign and the removal are saved together or not at all
    task_repository.unassign_member_tasks(db, project_id, user_id)
    project_repository.delete_member_from_project(db, project_member_to_be_deleted)
