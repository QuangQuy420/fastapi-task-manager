from datetime import datetime
from pydantic import BaseModel, Field
from app.core.enums import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    status: TaskStatus | None = TaskStatus.NEW.value
    priority: TaskPriority | None = TaskPriority.MEDIUM.value
    assigned_to: int | None = None
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    project_id: int
    sprint_id: int | None = None
    parent_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to: int | None = None
    sprint_id: int | None = None
    due_date: datetime | None = None


class TaskRead(TaskBase):
    id: int
    project_id: int
    sprint_id: int | None
    parent_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
