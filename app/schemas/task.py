from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import TaskStatus
from app.schemas.user import UserResponse


class TaskCreate(BaseModel):
    # status is not here: new tasks always start as "todo"
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    assignee_id: int | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str | None
    status: TaskStatus
    created_by_id: int
    created_at: datetime
    # nested like members: reads task.assignee, which is None for unassigned tasks
    assignee: UserResponse | None

class TaskUpdate(BaseModel):
    # every field is optional: only the fields the client sends are changed
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    # no null validator here on purpose: "assignee_id": null means unassign the task
    assignee_id: int | None = None
    
    @field_validator("title")
    @classmethod
    def title_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("title cannot be null")
        return value