from fastapi import APIRouter, status

from app.dependencies.auth import CurrentUser
from app.dependencies.database import DbSession
from app.dependencies.permissions import ProjectAsMember, ProjectAsOwner, TaskForProject
from app.enums import TaskStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import project_service, task_service

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

# get all members for a project: any member can see all members on the project
@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def get_members_for_project(project: ProjectAsMember, db: DbSession):
    return project_service.get_members_for_project(db, project.id)

# remove a member from project (only owners can remove any member or a member can remove himself)
@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member_from_project(
    user_id: int,                # {user_id} from the URL: the member to remove
    project: ProjectAsMember,    # reads {project_id}: 404 if missing or the caller isn't a member
    current_user: CurrentUser,   # the caller, from the token
    db: DbSession,
):
    project_service.delete_member_for_project(db, project.id, user_id, current_user)

@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, project: ProjectAsMember, current_user: CurrentUser, db: DbSession):
    return task_service.create_task(db, task, current_user, project.id)

@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
def get_tasks(project: ProjectAsMember, db: DbSession, status: TaskStatus | None = None):
    return task_service.get_tasks(db, project.id, status)

# update a task: the project owner, the task's creator or its assignee (only the fields sent)
@router.patch("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(data: TaskUpdate, task: TaskForProject, current_user: CurrentUser, db: DbSession):
    # TaskForProject reads {project_id} and {task_id}: 404 unless the caller is a member
    # and the task belongs to this project
    return task_service.update_task(db, task, data, current_user)
