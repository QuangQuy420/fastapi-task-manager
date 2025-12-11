from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.enums import ProjectStatus
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_user_projects(
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
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id, Project.deleted_at.is_(None))
        )

        if status:
            query = self.apply_filtering(query, {"status": status})

        if search:
            query = self.apply_searching(
                query,
                search_fields=["title", "description"],
                search_term=search,
            )

        query = self.apply_sorting(query, sort_by, order)

        return await self.get_paginated(query, page, page_size)

    async def get_project_detail(self, project_id: int) -> Project | None:
        query = (
            select(Project)
            .options(joinedload(Project.sprints))  # Eager load sprints
            .where(Project.id == project_id, Project.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return result.unique().scalars().first()

    async def delete_project(self, project: Project) -> None:
        await self.soft_delete(project)
        project.status = ProjectStatus.ARCHIVED.value
        await self.db.flush()
