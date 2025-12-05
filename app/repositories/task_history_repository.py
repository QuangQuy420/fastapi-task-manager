from typing import Iterable

from sqlalchemy.orm import Session

from app.models.task_history import TaskHistory


class TaskHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_snapshot(
        self,
        *,
        task_id: int,
        changed_by: int,
        action: str,
        snapshot: dict,
    ) -> TaskHistory:
        history = TaskHistory(
            task_id=task_id,
            changed_by=changed_by,
            action=action,
            **snapshot,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def list_for_task(self, task_id: int) -> Iterable[TaskHistory]:
        return (
            self.db.query(TaskHistory)
            .filter(TaskHistory.task_id == task_id)
            .order_by(TaskHistory.changed_at.desc())
            .all()
        )
