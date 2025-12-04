from datetime import datetime
from pydantic import BaseModel, Field
from app.core.enums import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None

    status: TaskStatus = TaskStatus.TODO.value
    priority: TaskPriority = TaskPriority.MEDIUM.value

    assigned_to: str | None = None
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    status: TaskStatus | None = None
    priority: TaskPriority | None = None

    assigned_to: str | None = None
    due_date: datetime | None = None
    is_completed: bool | None = None


class TaskOut(TaskBase):
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
