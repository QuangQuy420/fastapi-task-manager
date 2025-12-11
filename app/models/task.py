from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.core.enums import TaskPriority, TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sprint_id = Column(
        Integer,
        ForeignKey("sprints.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    title = Column(String(255), nullable=False, index=True)
    description = Column(String, nullable=True)

    status = Column(
        String(50), nullable=False, default=TaskStatus.TODO.value, index=True
    )
    priority = Column(
        Integer, nullable=False, default=TaskPriority.MEDIUM.value, index=True
    )
    due_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at = Column(DateTime, nullable=True, index=True)

    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], backref="children")
    assigned_user = relationship(
        "User", foreign_keys=[assigned_to], back_populates="tasks"
    )
    histories = relationship("TaskHistory", back_populates="task")
