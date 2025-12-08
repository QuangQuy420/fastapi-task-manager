from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import ProjectHistoryAction, UserRole
from app.repositories.history_project_repository import ProjectHistoryRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from sqlalchemy.exc import SQLAlchemyError


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)
        self.project_history_repo = ProjectHistoryRepository(db)

    def _check_permissions(self, project_id: int, user_id: int, required_roles: list[str]):
        member = self.member_repo.get_member_project(project_id, user_id)

        if not member or member.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to perfomm action",
            )

    def create_project(self, data: ProjectCreate, owner_id: int):
        try:
            project = self.project_repo.create_project(
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

            self.project_history_repo.create_history(
                meta={
                    "project_id": project.id,
                    "changed_by": owner_id,
                    "action": ProjectHistoryAction.CREATE.value,
                    "title": project.title,
                    "description": project.description,
                    "status": project.status,
                },
                details=None,
            )

            self.db.commit()
            self.db.refresh(project)

            return project
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_project_by_id(self, project_id: int, for_update: bool = False):
        project = self.project_repo.get_project_by_id(project_id, for_update)
        if not project or project.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    def update_project(self, project_id: int, data: ProjectUpdate, user_id: int):
        self._check_permissions(
            project_id,
            user_id,
            ["owner", "maintainer"],
        )

        project = self.get_project_by_id(project_id, for_update=True)
        
        update_data = data.model_dump(exclude_unset=True)
        before = {
            "title": project.title,
            "description": project.description,
            "status": project.status,
        }

        try:
            project = self.project_repo.update_project(project, update_data)

            after = {
                "title": project.title,
                "description": project.description,
                "status": project.status,
            }

            self.project_history_repo.create_history(
                meta={
                    "project_id": project.id,
                    "changed_by": user_id,
                    "action": ProjectHistoryAction.UPDATE.value,
                    "title": project.title,
                    "description": project.description,
                    "status": project.status,
                },
                details={
                    "before": before,
                    "after": after,
                },
            )

            self.db.commit()
            self.db.refresh(project)

            return project
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_project(self, project_id: int, user_id: int):
        self._check_permissions(
            project_id,
            user_id,
            ["owner"],
        )

        project = self.get_project_by_id(project_id, for_update=True)

        try:
            self.project_history_repo.create_history(
                meta={
                    "project_id": project.id,
                    "changed_by": user_id,
                    "action": ProjectHistoryAction.DELETE.value,
                    "title": project.title,
                    "description": project.description,
                    "status": project.status,
                },
                details=None,
            )
            self.project_repo.delete_project(project)

            self.db.commit()

            return None
        except SQLAlchemyError:
            self.db.rollback()
            raise
