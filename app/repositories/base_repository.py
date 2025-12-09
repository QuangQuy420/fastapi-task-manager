from typing import Generic, TypeVar, Type, Optional, List
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base) # type: ignore


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int, for_update: bool = False) -> Optional[ModelType]:
        """Get a single record by ID."""
        query = self.db.query(self.model).filter(self.model.id == id)
        if for_update:
            query = query.with_for_update()
        return query.first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

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