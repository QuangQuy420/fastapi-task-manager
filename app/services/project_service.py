import math
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.enums import EntityEnum, HistoryAction, UserRole
from app.core.helpers import get_total_pages
from app.repositories.project_history_repository import ProjectHistoryRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.base_service import BaseService


class ProjectService(BaseService[ProjectRepository]):
    def __init__(self, db: Session = Depends(get_db)):
        project_repo = ProjectRepository(db)
        super().__init__(db, project_repo)
        self.member_repo = ProjectMemberRepository(db)
        self.project_history_repo = ProjectHistoryRepository(db)

    def get_user_projects(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "asc",
    ) -> PaginatedResponse:
        """Get paginated, filtered, and sorted projects."""
        items, total = self.repository.get_user_projects(
            user_id=user_id,
            page=page,
            page_size=page_size,
            status=status,
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

    def get_project_detail(self, project_id: int, user_id: int):
        member = self.member_repo.get_member_project(project_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project",
            )
        detail_project = self.repository.get_project_detail(project_id)
        if not detail_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return detail_project

    def create_project(self, data: ProjectCreate, owner_id: int):
        project = self.repository.create(
            title=data.title,
            description=data.description,
            managed_by=owner_id,
        )
        self.db.flush()

        self.member_repo.add_member(
            project_id=project.id,
            user_id=owner_id,
            role=UserRole.OWNER.value,
        )

        self.project_history_repo.create(
            project_id=project.id,
            changed_by=owner_id,
            action=HistoryAction.CREATE.value,
            details=None
        )

        self.commit_or_rollback()
        return self.refresh(project)

    def update_project(self, project_id: int, data: ProjectUpdate, user_id: int):
        self.member_repo.check_permissions(project_id, user_id, [UserRole.OWNER.value, UserRole.MAINTAINER.value])

        project = self.get_by_id_or_404(entity_id=project_id, for_update=True, entity_name=EntityEnum.PROJECT.value)

        update_data = data.model_dump(exclude_unset=True)
        before = {
            "title": project.title,
            "description": project.description,
            "status": project.status,
        }

        project = self.repository.update(project, update_data)

        after = {
            "title": project.title,
            "description": project.description,
            "status": project.status,
        }

        self.project_history_repo.create(
            project_id=project.id,
            changed_by=user_id,
            action=HistoryAction.UPDATE.value,
            details={"before": before, "after": after},
        )

        self.commit_or_rollback()
        return self.refresh(project)

    def delete_project(self, project_id: int, user_id: int):
        self.member_repo.check_permissions(project_id, user_id, [UserRole.OWNER.value])

        project = self.get_by_id_or_404(entity_id=project_id, for_update=True, entity_name=EntityEnum.PROJECT.value)

        self.project_history_repo.create(
            project_id=project.id,
            changed_by=user_id,
            action=HistoryAction.DELETE.value,
            details=None,
        )

        self.repository.delete_project(project)
        self.commit_or_rollback()