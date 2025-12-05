from sqlalchemy.orm import Session

from app.repositories.task_history_repository import TaskHistoryRepository


class TaskHistoryService:
    def __init__(self, db: Session):
        self.db = db
        self.history_repo = TaskHistoryRepository(db)

    def get_task_history(self, task_id: int):
        return self.history_repo.list_for_task(task_id)
