from typing import Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)  # type: ignore


class BaseRepository(Generic[ModelType]):
    """Base repository with common Async CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int, for_update: bool = False) -> Optional[ModelType]:
        """Get a single record by ID."""
        query = select(self.model).where(self.model.id == id)

        if for_update:
            query = query.with_for_update()

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_paginated(
        self, query: Select, page: int = 1, page_size: int = 20
    ) -> Tuple[List[ModelType], int]:
        """
        Execute paginated query and return items + total count.
        Note: 'query' argument must be a SQLAlchemy 'select' object.
        """

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()

        return items, total

    def apply_filtering(self, query: Select, filters: dict) -> Select:
        """Apply filtering to query based on filters dict."""
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                column = getattr(self.model, field)
                query = query.where(column == value)
        return query

    def apply_searching(
        self, query: Select, search_fields: List[str], search_term: str
    ) -> Select:
        """Apply searching to query based on search fields and term."""
        if search_term:
            search_term = f"%{search_term}%"
            search_filters = [
                getattr(self.model, field).ilike(search_term)
                for field in search_fields
                if hasattr(self.model, field)
            ]
            if search_filters:
                query = query.where(or_(*search_filters))
        return query

    def apply_sorting(self, query: Select, sort_by: str, order: str = "desc") -> Select:
        """Apply sorting to query."""
        if hasattr(self.model, sort_by):
            column = getattr(self.model, sort_by)
            if order == "asc":
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))
        return query

    def create(self, **kwargs) -> ModelType:
        """
        Create a new record.
        Note: 'add' is sync, but we don't return the ID until 'flush' or 'commit'
        is called in the service layer.
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        return instance

    async def update(self, instance: ModelType, data: dict) -> ModelType:
        """Update an existing record."""
        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        await self.db.flush()
        return instance

    async def delete(self, instance: ModelType) -> None:
        """Hard delete a record."""
        await self.db.delete(instance)
        await self.db.flush()

    async def soft_delete(self, instance: ModelType) -> None:
        """Soft delete a record (if model has deleted_at)."""
        if hasattr(instance, "deleted_at"):
            instance.deleted_at = func.now()
            await self.db.flush()
        else:
            raise AttributeError(f"{self.model.__name__} does not support soft delete")

    async def count(self) -> int:
        """Count total records."""
        query = select(func.count()).select_from(self.model)
        return await self.db.scalar(query) or 0

    async def exists(self, id: int) -> bool:
        """Check if record exists."""
        query = select(self.model.id).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first() is not None
