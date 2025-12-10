from datetime import date, datetime
from pydantic import BaseModel, Field

from app.core.enums import SprintStatus


class SprintBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    status: SprintStatus | None = SprintStatus.NEW.value
    start_date: date
    end_date: date


class SprintCreate(SprintBase):
    pass


class SprintUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: SprintStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class SprintRead(SprintBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True