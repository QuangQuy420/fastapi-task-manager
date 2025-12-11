from typing import Generic, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EntityEnum
from app.repositories.base_repository import BaseRepository

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[RepositoryType]):
    """
    Base service with async transaction management and error handling.
    """

    def __init__(self, db: AsyncSession, repository: RepositoryType):
        self.db = db
        self.repository = repository

    async def get_by_id_or_404(
        self,
        entity_id: int,
        for_update: bool = False,
        entity_name: str = EntityEnum.Entity.value,
    ):
        """Get entity by ID or raise 404."""
        entity = await self.repository.get_by_id(entity_id, for_update)

        if not entity or getattr(entity, "deleted_at", None) is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{entity_name} not found or has been deleted",
            )
        return entity

    async def commit_or_rollback(self):
        """Commit transaction or rollback on error."""
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def flush_or_rollback(self):
        """Flush changes or rollback on error."""
        try:
            await self.db.flush()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def refresh(self, entity):
        """Refresh entity from database."""
        await self.db.refresh(entity)
        return entity
