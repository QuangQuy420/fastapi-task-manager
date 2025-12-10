from typing import List
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
)
def get_task_detail(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """Get task detail by ID."""
    return task_service.get_task_detail(task_id=task_id, user_id=current_user.id)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """Update a task."""
    return task_service.update_task(task_id=task_id, data=data, user_id=current_user.id)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """Delete a task."""
    task_service.delete_task(task_id=task_id, user_id=current_user.id)
    return None