from sqlalchemy.orm import Session

from app.models.task_history import TaskHistory
from app.repositories.base_repository import BaseRepository


class TaskHistoryRepository(BaseRepository[TaskHistory]):
    def __init__(self, db: Session):
        super().__init__(TaskHistory, db)
