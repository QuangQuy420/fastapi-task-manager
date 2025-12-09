from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.enums import EntityEnum, HistoryAction, UserRole
from app.core.helpers import format_date_to_string
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_history_repository import TaskHistoryRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.base_service import BaseService


class TaskService(BaseService[TaskRepository]):
    def __init__(self, db: Session = Depends(get_db)):
        task_repo = TaskRepository(db)
        super().__init__(db, task_repo)
        self.member_repo = ProjectMemberRepository(db)
        self.task_history_repo = TaskHistoryRepository(db)
        self.project_repo = ProjectRepository(db)

    def _validate_assigned_user(self, project_id: int, assigned_to: int | None):
        """Ensure assigned user is a project member."""
        if assigned_to is None:
            return
        
        is_member = self.member_repo.get_member_project(project_id, assigned_to)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign task to user who is not a project member",
            )

    def create_task(self, data: TaskCreate, user_id: int):
        """Create a new task."""
        self.member_repo.check_permissions(
            project_id=data.project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value, UserRole.MEMBER.value],
        )

        project = self.project_repo.get_by_id(id=data.project_id)
        if not project or getattr(project, "deleted_at", None) is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or has been deleted",
            )

        # Validate assigned_to is project member
        if data.assigned_to:
            self._validate_assigned_user(data.project_id, data.assigned_to)

        task_data = data.model_dump()

        task = self.repository.create(**task_data)
        self.db.flush()

        self.task_history_repo.create(
            task_id=task.id,
            changed_by=user_id,
            action=HistoryAction.CREATE.value,
            details=None,
        )

        self.commit_or_rollback()
        return self.refresh(task)

    def update_task(self, task_id: int, data: TaskUpdate, user_id: int):
        """Update an existing task."""
        task = self.get_by_id_or_404(entity_id=task_id, for_update=True, entity_name=EntityEnum.TASK.value)

        # Check permissions
        self.member_repo.check_permissions(
            project_id=task.project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value, UserRole.MEMBER.value],
        )

        update_data = data.model_dump(exclude_unset=True)

        # Validate if reassigning
        if update_data.get("assigned_to") is not None:
            self._validate_assigned_user(task.project_id, update_data["assigned_to"])

        before = {
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "due_date": format_date_to_string(task.due_date),
        }

        task = self.repository.update(task, update_data)

        # Capture after state
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
            details={"before": before, "after": after}
        )

        self.commit_or_rollback()
        return self.refresh(task)

    def delete_task(self, task_id: int, user_id: int):
        """Soft delete a task."""
        task = self.get_by_id_or_404(entity_id=task_id, for_update=True, entity_name=EntityEnum.TASK.value)

        # Check permissions
        self.member_repo.check_permissions(
            project_id=task.project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value, UserRole.MEMBER.value],
        )

        self.task_history_repo.create(
            task_id=task.id,
            changed_by=user_id,
            action=HistoryAction.DELETE.value,
            details=None,
        )

        self.repository.delete_task(task)
        self.commit_or_rollback()
