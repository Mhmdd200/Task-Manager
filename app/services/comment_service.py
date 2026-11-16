from sqlalchemy.orm import Session

from app.repositories import comment_repository
from app.schemas.comment import CommentCreate

# i could've done body instead of data but this is cleaner
def create_comment(db: Session, data: CommentCreate, author_id: int, task_id: int):
    return comment_repository.create_comment(db, task_id, author_id, data.body)
