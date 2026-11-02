from fastapi import APIRouter, status

from app.dependencies.auth import CurrentUser
from app.dependencies.database import DbSession
from app.dependencies.permissions import ProjectAsMember, ProjectAsOwner
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
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
    
@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def create_member(project: ProjectAsOwner, db: DbSession):
    # here the permissions are for owner. only owner can add a member
    # also an owner can add a member only not an owner. As i will leave setting user as owner
    # for another api. so check if the user is a member
    
