from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload

from app.core.enums import ProjectStatus
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_user_projects(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "asc",
    ) -> Tuple[List[Project], int]:
        """Get paginated, filtered, and sorted projects for a user."""
        query = (
            self.db.query(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .filter(ProjectMember.user_id == user_id, Project.deleted_at.is_(None))
        )

        # Apply filters
        if status:
            query = self.apply_filtering(query, {"status": status})

        # Apply searching
        if search:
            query = self.apply_searching(
                query,
                search_fields=["title", "description"],
                search_term=search,
            )

        # Apply sorting
        query = self.apply_sorting(query, sort_by, order)

        return self.get_paginated(query, page, page_size)

    def get_project_detail(self, project_id: int) -> Project:
        return (
            self.db.query(Project)
            .options(joinedload(Project.sprints))
            .filter(Project.id == project_id, Project.deleted_at.is_(None))
            .first()
        )

    def delete_project(self, project: Project) -> None:
        self.soft_delete(project)
        project.status = ProjectStatus.ARCHIVED.value
