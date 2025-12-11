from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SprintStatus
from app.models.sprint import Sprint
from app.repositories.base_repository import BaseRepository


class SprintRepository(BaseRepository[Sprint]):
    def __init__(self, db: AsyncSession):
        super().__init__(Sprint, db)

    async def get_project_sprints(
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
        query = select(Sprint).where(
            Sprint.project_id == project_id, Sprint.deleted_at.is_(None)
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
            query = query.where(Sprint.start_date >= start_date)

        if end_date:
            query = query.where(Sprint.end_date <= end_date)

        query = self.apply_sorting(query, sort_by, order)

        return await self.get_paginated(query, page, page_size)

    async def delete_sprint(self, sprint: Sprint) -> None:
        await self.soft_delete(sprint)
        sprint.status = SprintStatus.ARCHIVED.value
        await self.db.flush()

    async def get_sprint_by_id_and_project_id(
        self, sprint_id: int, project_id: int
    ) -> Optional[Sprint]:
        query = select(Sprint).where(
            Sprint.id == sprint_id,
            Sprint.project_id == project_id,
            Sprint.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalars().first()
