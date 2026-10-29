from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import CurrentUser
from app.dependencies.database import DbSession
from app.models.project import Project
from app.services import project_service


def get_project_as_member(
    project_id: int,            # read from the URL path: /projects/{project_id}
    current_user: CurrentUser,  # runs get_current_user first (401 if no valid token)
    db: DbSession,              # runs get_db
) -> Project:
    return project_service.get_project_for_member(db, project_id, current_user)


def get_project_as_owner(
    project_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Project:
    # this is the "IsOwner" permission: raises 404/403 if the rule fails,
    # otherwise hands the loaded project to the endpoint
    return project_service.get_project_for_owner(db, project_id, current_user)


ProjectAsMember = Annotated[Project, Depends(get_project_as_member)]
ProjectAsOwner = Annotated[Project, Depends(get_project_as_owner)]
