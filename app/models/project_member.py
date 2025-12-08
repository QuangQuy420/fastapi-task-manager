from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)

from app.core.db import Base
from app.core.enums import UserRole


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(20), nullable=False, default=UserRole.OWNER.value)  # owner/maintainer/member/viewer

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )
