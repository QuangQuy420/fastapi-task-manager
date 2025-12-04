from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from app.core.enums import TaskStatus


class TaskService:
    """
    Application service layer for Task-related business logic.
    """

    def __init__(self, db: Session):
        self.repo = TaskRepository(db)


    def _ensure_completed_flag(self, task_in: TaskUpdate | TaskCreate) -> dict:
        """
        Apply simple rule:
        - If status == DONE → is_completed = True
        - Otherwise, do not touch is_completed (let default or caller handle)
        Returns a dict of updated data.
        """
        data = task_in.model_dump(exclude_unset=True)

        status_value = data.get("status")
        if status_value is not None:
            if status_value == TaskStatus.DONE.value:
                data["is_completed"] = True

        return data

    def _get_or_404(self, task_id: int) -> Task:
        task = self.repo.get(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    # ---------- Public API used by routes ----------

    def list_tasks(self) -> list[Task]:
        """
        Return all tasks.
        Later you can add filters (status, priority, assigned_to, etc.)
        """
        return self.repo.list()

    def get_task(self, task_id: int) -> Task:
        """
        Return a single task or raise 404.
        """
        return self._get_or_404(task_id)

    def create_task(self, task_in: TaskCreate) -> Task:
        """
        Create a new task.
        Business rules:
        - If status == DONE → force is_completed = True.
        """
        data = self._ensure_completed_flag(task_in)

        task_in = TaskCreate(**data)
        return self.repo.create(task_in)

    def update_task(self, task_id: int, task_in: TaskUpdate) -> Task:
        """
        Update an existing task.
        Business rules:
        - If status == DONE → force is_completed = True.
        """
        task = self._get_or_404(task_id)
        data = self._ensure_completed_flag(task_in)

        task_in = TaskUpdate(**data)
        return self.repo.update(task, task_in)

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task by ID or raise 404 if it doesn't exist.
        """
        task = self._get_or_404(task_id)
        self.repo.delete(task)
