from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.enums import EntityEnum, HistoryAction, UserRole
from app.core.helpers import format_date_to_string, get_total_pages
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.sprint_history_repository import SprintHistoryRepository
from app.repositories.sprint_repository import SprintRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.sprint import SprintCreate, SprintUpdate
from app.services.base_service import BaseService


class SprintService(BaseService[SprintRepository]):
    def __init__(self, db: Session = Depends(get_db)):
        sprint_repo = SprintRepository(db)
        super().__init__(db, sprint_repo)
        self.member_repo = ProjectMemberRepository(db)
        self.sprint_history_repo = SprintHistoryRepository(db)
        self.project_repo = ProjectRepository(db)

    def get_sprint_detail(self, sprint_id: int, user_id: int):
        sprint = self.get_by_id_or_404(
            entity_id=sprint_id, entity_name=EntityEnum.SPRINT.value
        )

        self.member_repo.check_permissions(
            project_id=sprint.project_id,
            user_id=user_id,
            required_roles=[
                UserRole.OWNER.value,
                UserRole.MAINTAINER.value,
                UserRole.MEMBER.value,
                UserRole.VIEWER.value,
            ],
        )

        return sprint

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
        user_id: int = None,
    ):
        self.member_repo.check_permissions(
            project_id=project_id,
            user_id=user_id,
            required_roles=[
                UserRole.OWNER.value,
                UserRole.MAINTAINER.value,
                UserRole.MEMBER.value,
                UserRole.VIEWER.value,
            ],
        )

        items, total = self.repository.get_project_sprints(
            project_id=project_id,
            page=page,
            page_size=page_size,
            status=status,
            search=search,
            start_date=start_date,
            end_date=end_date,
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

    def create_sprint(self, project_id: int, data: SprintCreate, user_id: int):
        self.member_repo.check_permissions(
            project_id=project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value],
        )

        project = self.project_repo.get_by_id(id=project_id)
        if not project or getattr(project, "deleted_at", None) is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or has been deleted",
            )

        sprint_data = data.model_dump()
        sprint_data["project_id"] = project_id

        sprint = self.repository.create(**sprint_data)
        self.db.flush()

        self.sprint_history_repo.create(
            sprint_id=sprint.id,
            changed_by=user_id,
            action=HistoryAction.CREATE.value,
            details=None,
        )

        self.commit_or_rollback()
        return sprint

    def update_sprint(self, sprint_id: int, data: SprintUpdate, user_id: int):
        sprint = self.get_by_id_or_404(
            entity_id=sprint_id, for_update=True, entity_name=EntityEnum.SPRINT.value
        )

        self.member_repo.check_permissions(
            project_id=sprint.project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value],
        )

        update_data = data.model_dump(exclude_unset=True)

        before = {
            "title": sprint.title,
            "description": sprint.description,
            "status": sprint.status,
            "start_date": format_date_to_string(sprint.start_date),
            "end_date": format_date_to_string(sprint.end_date),
        }

        sprint = self.repository.update(sprint, update_data)

        after = {
            "title": sprint.title,
            "description": sprint.description,
            "status": sprint.status,
            "start_date": format_date_to_string(sprint.start_date),
            "end_date": format_date_to_string(sprint.end_date),
        }

        self.sprint_history_repo.create(
            sprint_id=sprint.id,
            changed_by=user_id,
            action=HistoryAction.UPDATE.value,
            details={"before": before, "after": after},
        )

        self.commit_or_rollback()
        return self.refresh(sprint)

    def delete_sprint(self, sprint_id: int, user_id: int):
        sprint = self.get_by_id_or_404(
            entity_id=sprint_id, for_update=True, entity_name=EntityEnum.SPRINT.value
        )

        self.member_repo.check_permissions(
            project_id=sprint.project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value],
        )

        self.sprint_history_repo.create(
            sprint_id=sprint.id,
            changed_by=user_id,
            action=HistoryAction.DELETE.value,
            details=None,
        )

        self.repository.delete_sprint(sprint)
        self.commit_or_rollback()
