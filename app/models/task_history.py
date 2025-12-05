from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    func,
)

from app.core.db import Base

class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())
    action = Column(String(20), nullable=False)  # "create", "update", "status_change"

    title = Column(String(255))
    description = Column(String)
    status = Column(String(50))
    priority = Column(Integer)
    assigned_to = Column(String(255))
    due_date = Column(DateTime)
    is_completed = Column(Boolean)
