from pydantic import BaseModel, ConfigDict

from app.enums import Role
from app.schemas.user import UserResponse


class ProjectMemberCreate(BaseModel):
    # project_id comes from the URL and role is always "member",
    # so the client only chooses which user to add
    user_id: int

class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    user: UserResponse
    role: Role
    