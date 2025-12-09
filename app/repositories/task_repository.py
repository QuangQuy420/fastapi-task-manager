from typing import Iterable
from sqlalchemy.orm import Session

from app.core.enums import TaskStatus
from app.models.task import Task
from app.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_project_tasks(self, project_id: int) -> Iterable[Task]:
        return (
            self.db.query(Task)
            .filter(
                Task.project_id == project_id,
                Task.deleted_at.is_(None)
            )
            .order_by(Task.created_at.desc())
            .all()
        )

    def get_sprint_tasks(self, sprint_id: int) -> Iterable[Task]:
        return (
            self.db.query(Task)
            .filter(
                Task.sprint_id == sprint_id,
                Task.deleted_at.is_(None)
            )
            .all()
        )

    def delete_task(self, task: Task) -> None:
        self.soft_delete(task)
        task.status = TaskStatus.ACHIEVED.value