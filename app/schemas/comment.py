from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user import UserResponse


class CommentCreate(BaseModel):
    # only body: the task comes from the URL and the author comes from the token
    body: str = Field(min_length=1, max_length=1000)

    @field_validator("body")
    @classmethod
    def body_cannot_be_blank(cls, value):
        # min_length alone would accept "   "
        if not value.strip():
            raise ValueError("body cannot be blank")
        return value


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    body: str
    created_at: datetime
    # nested like TaskResponse.assignee: reads comment.author
    author: UserResponse


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int
