from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.task_history import TaskHistory


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, task_id: int) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def save(self, task: Task):
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def add_history(
        self,
        task: Task,
        changed_by: int,
        action: str,
    ):
        history = TaskHistory(
            task_id=task.id,
            changed_by=changed_by,
            action=action,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assigned_to=task.assigned_to,
            due_date=task.due_date,
            is_completed=task.is_completed,
        )
        self.db.add(history)
