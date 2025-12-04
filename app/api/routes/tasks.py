from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# --- Dependency: DB Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Dependency: TaskService ---
def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


# -----------------------------
#       ROUTES (ASYNC)
# -----------------------------

@router.get("/", response_model=List[TaskOut])
async def list_tasks(service: TaskService = Depends(get_task_service)):
    """
    Return all tasks.
    """
    return service.list_tasks()


@router.post(
    "/",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    """
    Create a new task.
    """
    return service.create_task(task_in)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """
    Get a task by ID.
    """
    return service.get_task(task_id)


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """
    Update a task completely.
    """
    return service.update_task(task_id, task_in)


@router.patch("/{task_id}", response_model=TaskOut)
async def partial_update_task(
    task_id: int,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """
    Partially update a task (PATCH).
    """
    return service.update_task(task_id, task_in)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """
    Delete a task by ID.
    """
    service.delete_task(task_id)
    return None
