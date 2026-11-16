from sqlalchemy.orm import Session

from app.models.comment import Comment


def create_comment(db: Session, task_id: int, author_id: int, body: str) -> Comment:
    comment = Comment(
                task_id=task_id,
                author_id=author_id,
                body=body
            )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
