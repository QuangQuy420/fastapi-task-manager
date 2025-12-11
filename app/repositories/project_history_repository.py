from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_history import ProjectHistory
from app.repositories.base_repository import BaseRepository


class ProjectHistoryRepository(BaseRepository[ProjectHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectHistory, db)
