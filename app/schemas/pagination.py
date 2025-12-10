from typing import Generic, Optional, TypeVar, List
from pydantic import BaseModel, Field

from app.core.enums import ProjectSortBy, SortOrder

T = TypeVar("T")


class ProjectFilterParams(BaseModel):
    """Filter parameters for projects."""
    status: Optional[str] = None
    search: Optional[str] = Field(None, description="Search in title/description")


class ProjectSortParams(BaseModel):
    """Sort parameters for projects."""
    sort_by: ProjectSortBy = ProjectSortBy.CREATED_AT
    order: SortOrder = SortOrder.DESC


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True