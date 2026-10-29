from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import Role
from app.models.project import Project
from app.models.project_members import ProjectMember


def get_by_id(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)

def get_all_projects_for_user(db: Session, user_id: int) -> list[Project]:
    query = select(Project).join(ProjectMember, Project.id==ProjectMember.project_id).where(ProjectMember.user_id==user_id)
    return db.scalars(query).all()

def create(db: Session, name: str, description: str | None, user_id: int) -> Project:
    project = Project(
        name=name,
        description=description,
        owner_id=user_id
    )
    db.add(project)
    # applies/sends the pending SQL changes to the database, but it does not permanently commit them
    db.flush()
    # create the user with owner role
    project_member = ProjectMember(
        project_id=project.id,
        user_id=user_id,
        role=Role.OWNER
    )
    db.add(project_member)
    db.commit()
    db.refresh(project)
    return project

def update(db: Session, project: Project, updates: dict) -> Project:
    for field, value in updates.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project

def delete(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
    
def get_member(db: Session, project_id: int, user_id: int) -> ProjectMember | None:
    query = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    )
    return db.scalar(query)

def add_member(db: Session, project_id: int, user_id: int, role: Role = Role.MEMBER) -> ProjectMember:
    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member