from pydantic import BaseModel, ConfigDict

from app.enums import Role


class ProjectMemberCreate(BaseModel):
    project_id: int
    user_id: int
    role: Role
    
class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    user_id: int
    role: Role
    