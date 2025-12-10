from typing import Optional
from sqlalchemy.orm import Session

from app.core.enums import SprintStatus
from app.models.sprint import Sprint
from app.repositories.base_repository import BaseRepository


class SprintRepository(BaseRepository[Sprint]):
    def __init__(self, db: Session):
        super().__init__(Sprint, db)
    
    def get_project_sprints(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "asc",
    ):
        query = (
            self.db.query(Sprint)
            .filter(
                Sprint.project_id == project_id,
                Sprint.deleted_at.is_(None)
            )
        )

        if status:
            query = self.apply_filtering(query, {"status": status})
        
        if search:
            query = self.apply_searching(
                query,
                search_fields=["title", "description"],
                search_term=search,
            )
        
        if start_date:
            query = query.filter(Sprint.start_date >= start_date)
        
        if end_date:
            query = query.filter(Sprint.end_date <= end_date)
        
        query = self.apply_sorting(query, sort_by, order)
        
        return self.get_paginated(query, page, page_size)

    def delete_sprint(self, sprint: Sprint) -> None:
        self.soft_delete(sprint)
        sprint.status = SprintStatus.ARCHIVED.value

    def get_sprint_by_id_and_project_id(self, sprint_id: int, project_id: int) -> Optional[Sprint]:
        return (
            self.db.query(Sprint)
            .filter(
                Sprint.id == sprint_id,
                Sprint.project_id == project_id,
                Sprint.deleted_at.is_(None)
            )
            .first()
        )