from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.enums import EntityEnum, HistoryAction, UserRole
from app.core.helpers import format_date_to_string, get_total_pages
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.sprint_repository import SprintRepository
from app.repositories.task_history_repository import TaskHistoryRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.base_service import BaseService


class TaskService(BaseService[TaskRepository]):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        task_repo = TaskRepository(db)
        super().__init__(db, task_repo)
        self.member_repo = ProjectMemberRepository(db)
        self.task_history_repo = TaskHistoryRepository(db)
        self.project_repo = ProjectRepository(db)
        self.sprint_repo = SprintRepository(db)

    async def _validate_assigned_user(self, project_id: int, assigned_to: int | None):
        """Ensure assigned user is a project member."""
        if assigned_to is None:
            return

        is_member = await self.member_repo.get_member_project(project_id, assigned_to)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign task to user who is not a project member",
            )

    async def _validate_assigned_sprint(self, project_id: int, sprint_id: int):
        """Ensure assigned sprint belongs to the project."""
        sprint = await self.sprint_repo.get_sprint_by_id_and_project_id(
            sprint_id, project_id
        )

        if not sprint:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned sprint does not belong to the project",
            )

    async def get_task_detail(self, task_id: int, user_id: int):
        """Get task detail by ID."""
        task = await self.get_by_id_or_404(
            entity_id=task_id, entity_name=EntityEnum.TASK.value
        )

        await self.member_repo.check_permissions(
            project_id=task.project_id,
            user_id=user_id,
            required_roles=[
                UserRole.OWNER.value,
                UserRole.MAINTAINER.value,
                UserRole.MEMBER.value,
                UserRole.VIEWER.value,
            ],
        )

        return task

    async def get_project_tasks(
        self,
        project_id: int,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None,
        sprint_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "asc",
    ):
        """Get paginated, filtered, and sorted tasks."""
        await self.member_repo.check_permissions(
            project_id=project_id,
            user_id=user_id,
            required_roles=[
                UserRole.OWNER.value,
                UserRole.MAINTAINER.value,
                UserRole.MEMBER.value,
            ],
        )

        items, total = await self.repository.get_project_tasks(
            project_id=project_id,
            user_id=user_id,
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            sprint_id=sprint_id,
            search=search,
            sort_by=sort_by,
            order=order,
        )

        total_pages = get_total_pages(total, page_size)

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_task(self, project_id: int, data: TaskCreate, user_id: int):
        """Create a new task."""
        await self.member_repo.check_permissions(
            project_id=project_id,
            user_id=user_id,
            required_roles=[
                UserRole.OWNER.value,
                UserRole.MAINTAINER.value,
                UserRole.MEMBER.value,
            ],
        )

        project = await self.project_repo.get_by_id(id=project_id)
        if not project or getattr(project, "deleted_at", None) is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or has been deleted",
            )

        if data.assigned_to:
            await self._validate_assigned_user(project_id, data.assigned_to)

        if data.sprint_id:
            await self._validate_assigned_sprint(project_id, data.sprint_id)

        task_data = data.model_dump()

        task = self.repository.create(**task_data)

        await self.db.flush()

        self.task_history_repo.create(
            task_id=task.id,
            changed_by=user_id,
            action=HistoryAction.CREATE.value,
            details=None,
        )

        await self.commit_or_rollback()
        return await self.refresh(task)

    async def update_task(self, task_id: int, data: TaskUpdate, user_id: int):
        """Update an existing task."""
        task = await self.get_by_id_or_404(
            entity_id=task_id, for_update=True, entity_name=EntityEnum.TASK.value
        )

        await self.member_repo.check_permissions(
            project_id=task.project_id,
            user_id=user_id,
            required_roles=[
                UserRole.OWNER.value,
                UserRole.MAINTAINER.value,
                UserRole.MEMBER.value,
            ],
        )

        update_data = data.model_dump(exclude_unset=True)

        if update_data.get("assigned_to") is not None:
            await self._validate_assigned_user(
                task.project_id, update_data["assigned_to"]
            )

        before = {
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "due_date": format_date_to_string(task.due_date),
        }

        task = await self.repository.update(task, update_data)

        after = {
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "due_date": format_date_to_string(task.due_date),
        }

        self.task_history_repo.create(
            task_id=task.id,
            changed_by=user_id,
            action=HistoryAction.UPDATE.value,
            details={"before": before, "after": after},
        )

        await self.commit_or_rollback()
        return await self.refresh(task)

    async def delete_task(self, task_id: int, user_id: int):
        """Soft delete a task."""

        task = await self.get_by_id_or_404(
            entity_id=task_id, for_update=True, entity_name=EntityEnum.TASK.value
        )

        await self.member_repo.check_permissions(
            project_id=task.project_id,
            user_id=user_id,
            required_roles=[
                UserRole.OWNER.value,
                UserRole.MAINTAINER.value,
                UserRole.MEMBER.value,
            ],
        )

        self.task_history_repo.create(
            task_id=task.id,
            changed_by=user_id,
            action=HistoryAction.DELETE.value,
            details=None,
        )

        await self.repository.delete_task(task)
        await self.commit_or_rollback()
