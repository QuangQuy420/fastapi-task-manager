from typing import Optional
from fastapi import APIRouter, Depends, status, Query

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.sprint import SprintCreate, SprintRead, SprintUpdate
from app.schemas.task import TaskRead
from app.services.sprint_service import SprintService
from app.services.task_service import TaskService


router = APIRouter(prefix="/sprints", tags=["sprints"])

@router.get(
    "/{sprint_id}",
    response_model=SprintRead,
    status_code=status.HTTP_200_OK,
)
def get_sprint_detail(
    sprint_id: int,
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(),
):
    """
    Get sprint detail by ID.
    """
    return sprint_service.get_sprint_detail(sprint_id=sprint_id, user_id=current_user.id)


@router.patch(
    "/{sprint_id}",
    response_model=SprintRead,
    status_code=status.HTTP_200_OK,
)
def update_sprint(
    sprint_id: int,
    data: SprintUpdate,
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(),
):
    """
    Update an existing sprint.
    """
    return sprint_service.update_sprint(sprint_id=sprint_id, data=data, user_id=current_user.id)


@router.delete(
    "/{sprint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sprint(
    sprint_id: int,
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(),
):
    """
    Delete a sprint.
    """
    sprint_service.delete_sprint(sprint_id=sprint_id, user_id=current_user.id)


# Nested routes for tasks within a sprint
@router.get(
    "/{sprint_id}/tasks",
    response_model=PaginatedResponse[TaskRead],
    status_code=status.HTTP_200_OK,
)
def list_sprint_tasks(
    sprint_id: int,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    priority: Optional[int] = Query(default=None, description="Filter by priority"),
    assigned_to: Optional[int] = Query(default=None, description="Filter by assigned user"),
    search: Optional[str] = Query(default=None, description="Search in title/description"),
    sort_by: str = Query(default="created_at", description="Sort by field"),
    order: str = Query(default="desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """List all tasks in a sprint with filtering and pagination."""
    return task_service.get_sprint_tasks(
        sprint_id=sprint_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        search=search,
        sort_by=sort_by,
        order=order,
    )