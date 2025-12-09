from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.enums import EntityEnum, HistoryAction, UserRole
from app.core.helpers import format_date_to_string
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.sprint_history_repository import SprintHistoryRepository
from app.repositories.sprint_repository import SprintRepository
from app.schemas.sprint import SprintCreate, SprintUpdate
from app.services.base_service import BaseService


class SprintService(BaseService[SprintRepository]):
    def __init__(self, db: Session = Depends(get_db)):
        sprint_repo = SprintRepository(db)
        super().__init__(db, sprint_repo)
        self.member_repo = ProjectMemberRepository(db)
        self.sprint_history_repo = SprintHistoryRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_sprint(self, data: SprintCreate, user_id: int):
        self.member_repo.check_permissions(
            project_id=data.project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value],
        )

        project = self.project_repo.get_by_id(id=data.project_id)
        if not project or getattr(project, "deleted_at", None) is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found or has been deleted",
            )

        sprint_data = data.model_dump()

        sprint = self.repository.create(**sprint_data)
        self.db.flush()

        self.sprint_history_repo.create(
            sprint_id=sprint.id,
            changed_by=user_id,
            action=HistoryAction.CREATE.value,
            details=None
        )

        self.commit_or_rollback()
        return sprint

    def update_sprint(self, sprint_id: int, data: SprintUpdate, user_id: int):
        sprint = self.get_by_id_or_404(entity_id=sprint_id, for_update=True, entity_name=EntityEnum.SPRINT.value)
        
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
        sprint = self.get_by_id_or_404(entity_id=sprint_id, for_update=True, entity_name=EntityEnum.SPRINT.value)

        self.member_repo.check_permissions(
            project_id=sprint.project_id,
            user_id=user_id,
            required_roles=[UserRole.OWNER.value, UserRole.MAINTAINER.value],
        )

        self.sprint_history_repo.create(
            sprint_id=sprint.id,
            changed_by=user_id,
            action=HistoryAction.DELETE.value,
            details=None
        )

        self.repository.delete_sprint(sprint)
        self.commit_or_rollback()
