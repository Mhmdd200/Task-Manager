from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from sqlalchemy import Enum as SAEnum

from app.enums import TaskStatus


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(
            TaskStatus,
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=TaskStatus.TODO,
    )
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assignee_id])
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )