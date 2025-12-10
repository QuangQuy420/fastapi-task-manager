from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base


class SprintHistory(Base):
    __tablename__ = "sprint_history"

    id = Column(Integer, primary_key=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=False, index=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())
    action = Column(String(20), nullable=False)

    details = Column(JSONB, nullable=True)

    sprint = relationship("Sprint", back_populates="histories")
