from typing import Generic, TypeVar
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.enums import EntityEnum
from app.repositories.base_repository import BaseRepository

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[RepositoryType]):
    """
    Base service with common transaction management and error handling.
    """

    def __init__(self, db: Session, repository: RepositoryType):
        self.db = db
        self.repository = repository

    def get_by_id_or_404(self, entity_id: int, for_update: bool = False, entity_name: str = EntityEnum.Entity.value):
        """Get entity by ID or raise 404."""
        entity = self.repository.get_by_id(entity_id, for_update)
        if not entity or getattr(entity, "deleted_at", None) is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{entity_name} not found or has been deleted",
            )
        return entity

    def commit_or_rollback(self):
        """Commit transaction or rollback on error."""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def flush_or_rollback(self):
        """Flush changes or rollback on error."""
        try:
            self.db.flush()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    def refresh(self, entity):
        """Refresh entity from database."""
        self.db.refresh(entity)
        return entity