from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)
from app.core.db import Base
from app.core.enums import TaskPriority, TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)

    status = Column(String(50), nullable=False, default=TaskStatus.TODO.value)
    priority = Column(Integer, nullable=False, default=TaskPriority.MEDIUM.value)
    assigned_to = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=True)

    is_completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(),
        onupdate=datetime.now(),
    )
