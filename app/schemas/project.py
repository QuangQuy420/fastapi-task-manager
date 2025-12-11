from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProjectStatus
from app.schemas.sprint import SprintRead


# ---- Project ----
class ProjectBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    status: ProjectStatus | None = ProjectStatus.PLANNED.value


class ProjectCreate(ProjectBase):
    pass  # managed_by will come from current_user in service


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int
    managed_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailRead(ProjectRead):
    sprints: List[SprintRead] = []

    model_config = ConfigDict(from_attributes=True)


# ---- ProjectMember ----
class ProjectMemberBase(BaseModel):
    project_id: int
    user_id: int
    role: str = "member"


class ProjectMemberCreate(ProjectMemberBase):
    pass


class ProjectMemberRead(ProjectMemberBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
