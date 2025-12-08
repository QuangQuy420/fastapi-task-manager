from datetime import datetime, date
from pydantic import BaseModel, Field

from app.core.enums import ProjectStatus


# ---- Project ----
class ProjectBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    status: str | None = ProjectStatus.PLANNED.value


class ProjectCreate(ProjectBase):
    pass  # managed_by will come from current_user in service


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int
    managed_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---- Sprint ----
class SprintBase(BaseModel):
    name: str
    goal: str | None = None
    status: str | None = "planned"
    start_date: date
    end_date: date


class SprintCreate(SprintBase):
    project_id: int


class SprintUpdate(BaseModel):
    name: str | None = None
    goal: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class SprintRead(SprintBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


# ---- TaskHistory ----
class TaskHistoryRead(BaseModel):
    id: int
    task_id: int
    changed_by: int
    changed_at: datetime
    action: str

    title: str | None
    description: str | None
    status: str | None
    priority: int | None
    assigned_to: str | None
    due_date: datetime | None
    is_completed: bool | None

    class Config:
        from_attributes = True
