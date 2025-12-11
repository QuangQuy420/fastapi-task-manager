from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TaskStatus
from app.models.task import Task
from app.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_project_tasks(
        self,
        project_id: int,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        assigned_to: Optional[int] = None,
        sprint_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "asc",
    ):
        query = select(Task).where(
            Task.project_id == project_id, Task.deleted_at.is_(None)
        )

        if status:
            query = self.apply_filtering(query, {"status": status})

        if priority:
            query = self.apply_filtering(query, {"priority": priority})

        if assigned_to:
            query = self.apply_filtering(query, {"assigned_to": assigned_to})

        if sprint_id:
            query = self.apply_filtering(query, {"sprint_id": sprint_id})

        if search:
            query = self.apply_searching(
                query,
                search_fields=["title", "description"],
                search_term=search,
            )

        query = self.apply_sorting(query, sort_by, order)

        return await self.get_paginated(query, page, page_size)

    async def get_sprint_tasks(self, sprint_id: int) -> List[Task]:
        query = select(Task).where(
            Task.sprint_id == sprint_id, Task.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_task(self, task: Task) -> None:
        await self.soft_delete(task)
        task.status = TaskStatus.ACHIEVED.value
        await self.db.flush()
