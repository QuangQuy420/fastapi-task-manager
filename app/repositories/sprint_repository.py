from sqlalchemy.orm import Session

from app.core.enums import SprintStatus
from app.models.sprint import Sprint
from app.repositories.base_repository import BaseRepository


class SprintRepository(BaseRepository[Sprint]):
    def __init__(self, db: Session):
        super().__init__(Sprint, db)

    def delete_sprint(self, sprint: Sprint) -> None:
        self.soft_delete(sprint)
        sprint.status = SprintStatus.ARCHIVED.value