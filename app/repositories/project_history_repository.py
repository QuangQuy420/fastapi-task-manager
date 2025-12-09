from sqlalchemy.orm import Session
from app.models.project_history import ProjectHistory
from app.repositories.base_repository import BaseRepository


class ProjectHistoryRepository(BaseRepository[ProjectHistory]):
    def __init__(self, db: Session):
        super().__init__(ProjectHistory, db)
