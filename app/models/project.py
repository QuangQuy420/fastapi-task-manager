from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.core.db import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    managed_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    sprints = relationship("Sprint", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
