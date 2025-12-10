from typing import Optional
from fastapi import APIRouter, Depends, status, Query

from app.api.deps import get_current_user
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailRead,
    ProjectUpdate,
    ProjectRead,
)
from app.schemas.sprint import SprintCreate, SprintRead
from app.schemas.task import TaskCreate, TaskRead
from app.services.project_service import ProjectService
from app.models.user import User
from app.services.sprint_service import SprintService
from app.services.task_service import TaskService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """Create a new project. Returns single resource."""
    return project_service.create_project(data, owner_id=current_user.id)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectRead],
    status_code=status.HTTP_200_OK,
)
def list_my_projects(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    search: Optional[str] = Query(
        default=None, description="Search in title/description"
    ),
    sort_by: str = Query(default="created_at", description="Sort by field"),
    order: str = Query(default="asc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """
    List projects with pagination, filtering, and sorting.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status**: Filter by project status (optional)
    - **search**: Search in title/description (optional)
    - **sort_by**: Sort field (default: created_at)
    - **order**: Sort order: asc or desc (default: asc)
    """
    return project_service.get_user_projects(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        search=search,
        sort_by=sort_by,
        order=order,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailRead,
    status_code=status.HTTP_200_OK,
)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """Get a single project. No pagination needed."""
    return project_service.get_project_detail(project_id, current_user.id)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """Update a project. Returns single updated resource."""
    return project_service.update_project(
        project_id=project_id,
        data=data,
        user_id=current_user.id,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(),
):
    """Delete a project. No response content."""
    project_service.delete_project(
        project_id=project_id,
        user_id=current_user.id,
    )
    return None


# Nested routes for sprints
@router.get(
    "/{project_id}/sprints",
    response_model=PaginatedResponse[SprintRead],
    status_code=status.HTTP_200_OK,
)
def list_project_sprints(
    project_id: int,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    search: Optional[str] = Query(
        default=None, description="Search in title/description"
    ),
    start_date: Optional[str] = Query(default=None, description="Filter by start date"),
    end_date: Optional[str] = Query(default=None, description="Filter by end date"),
    sort_by: str = Query(default="created_at", description="Sort by field"),
    order: str = Query(default="asc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(),
):
    """
    List sprints for a specific project with pagination.

    - **project_id**: ID of the project
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status**: Filter by sprint status (optional)
    - **search**: Search in title/description (optional)
    - **start_date**: Filter by start date (optional)
    - **end_date**: Filter by end date (optional)
    - **sort_by**: Sort field (default: created_at)
    - **order**: Sort order: asc or desc (default: asc)
    """
    return sprint_service.get_project_sprints(
        project_id=project_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        search=search,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        order=order,
    )


@router.post(
    "/{project_id}/sprints",
    response_model=SprintRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sprint(
    project_id: int,
    data: SprintCreate,
    current_user: User = Depends(get_current_user),
    sprint_service: SprintService = Depends(),
):
    """Create a new sprint within a specific project."""
    return sprint_service.create_sprint(
        project_id=project_id,
        data=data,
        user_id=current_user.id,
    )


# Nested routes for Tasks
@router.get(
    "/{project_id}/tasks",
    response_model=PaginatedResponse[TaskRead],
    status_code=status.HTTP_200_OK,
)
def list_project_tasks(
    project_id: int,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    priority: Optional[int] = Query(default=None, description="Filter by priority"),
    assigned_to: Optional[int] = Query(
        default=None, description="Filter by assigned user"
    ),
    sprint_id: Optional[int] = Query(default=None, description="Filter by sprint"),
    search: Optional[str] = Query(
        default=None, description="Search in title/description"
    ),
    sort_by: str = Query(default="created_at", description="Sort by field"),
    order: str = Query(default="desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    List all tasks in a project with advanced filtering and pagination.
    """
    return task_service.get_project_tasks(
        project_id=project_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        sprint_id=sprint_id,
        search=search,
        sort_by=sort_by,
        order=order,
    )


@router.post(
    "/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """Create a new task in a project."""
    # Override project_id from URL
    data.project_id = project_id
    return task_service.create_task(
        data=data, project_id=project_id, user_id=current_user.id
    )
