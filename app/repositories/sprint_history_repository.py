from sqlalchemy.orm import Session
from app.models.sprint_history import SprintHistory
from app.repositories.base_repository import BaseRepository


class SprintHistoryRepository(BaseRepository[SprintHistory]):
    def __init__(self, db: Session):
        super().__init__(SprintHistory, db)
