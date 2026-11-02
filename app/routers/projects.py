from fastapi import APIRouter, status

from app.dependencies.auth import CurrentUser
from app.dependencies.database import DbSession
from app.dependencies.permissions import ProjectAsMember, ProjectAsOwner
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberResponse
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(data: ProjectUpdate, project: ProjectAsOwner, db: DbSession):
    # by the time we get here the user is authenticated AND is the owner,
    # otherwise the dependency already returned 401 / 404 / 403
    return project_service.update_project(db, project, data)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(user: CurrentUser, data: ProjectCreate, db: DbSession):
    return project_service.create_project(db, data, user)

@router.get("", response_model=list[ProjectResponse])
def get_projects(user: CurrentUser, db: DbSession):
    return project_service.get_projects_for_user(db, user)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(project: ProjectAsMember):
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project: ProjectAsOwner, db: DbSession):
    project_service.delete_project(db, project)
    
@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(data: ProjectMemberCreate, project: ProjectAsOwner, db: DbSession):
    # ProjectAsOwner already checked the project from the URL, so we pass that
    # same project down instead of trusting any project_id from the body
    return project_service.add_member(db, project, data.user_id)
