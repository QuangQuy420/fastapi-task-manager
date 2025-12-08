from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

class ProjectHistory(Base):
    __tablename__ = "project_history"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())
    action = Column(String(20), nullable=False)

    title = Column(String(255))
    description = Column(String)
    status = Column(String(50))

    details = Column(JSONB, nullable=True)
