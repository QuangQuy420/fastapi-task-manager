from typing import Generic, TypeVar, Type, Optional, List, Tuple
from sqlalchemy.orm import Session, Query
from sqlalchemy import func, or_, asc, desc

from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base) # type: ignore


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int, for_update: bool = False) -> Optional[ModelType]:
        """Get a single record by ID."""
        query = self.db.query(self.model).filter(self.model.id == id)
        if for_update:
            query = query.with_for_update()
        return query.first()

    def get_paginated(
        self, 
        query: Query, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[ModelType], int]:
        """Execute paginated query and return items + total count."""
        total = query.count()
        skip = (page - 1) * page_size
        items = query.offset(skip).limit(page_size).all()
        return items, total

    def apply_filtering(
        self,
        query: Query,
        filters: dict
    ) -> Query:
        """Apply filtering to query based on filters dict."""
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                column = getattr(self.model, field)
                query = query.filter(column == value)
        return query
    
    def apply_searching(
        self,
        query: Query,
        search_fields: List[str],
        search_term: str
    ) -> Query:
        """Apply searching to query based on search fields and term."""
        if search_term:
            search_term = f"%{search_term}%"
            search_filters = [
                getattr(self.model, field).ilike(search_term)
                for field in search_fields
                if hasattr(self.model, field)
            ]
            if search_filters:
                query = query.filter(or_(*search_filters))
        return query

    def apply_sorting(
        self,
        query: Query,
        sort_by: str,
        order: str = "desc"
    ) -> Query:
        """Apply sorting to query."""
        if hasattr(self.model, sort_by):
            column = getattr(self.model, sort_by)
            if order == "asc":
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))
        return query

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        return instance

    def update(self, instance: ModelType, data: dict) -> ModelType:
        """Update an existing record."""
        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        self.db.flush()
        return instance

    def delete(self, instance: ModelType) -> None:
        """Hard delete a record."""
        self.db.delete(instance)
        self.db.flush()

    def soft_delete(self, instance: ModelType) -> None:
        """Soft delete a record (if model has deleted_at)."""
        if hasattr(instance, "deleted_at"):
            instance.deleted_at = func.now()
            self.db.flush()
        else:
            raise AttributeError(f"{self.model.__name__} does not support soft delete")

    def count(self) -> int:
        """Count total records."""
        return self.db.query(func.count(self.model.id)).scalar()

    def exists(self, id: int) -> bool:
        """Check if record exists."""
        return self.db.query(
            self.db.query(self.model).filter(self.model.id == id).exists()
        ).scalar()