from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import relationship

from app.core.db import Base


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default="planned")

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    who_can_update = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="Optional override; otherwise use project_members",
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")

    __table_args__ = (
        Index(
            "ix_sprints_project_status_dates",
            "project_id",
            "status",
            "start_date",
            "end_date",
        ),
    )
