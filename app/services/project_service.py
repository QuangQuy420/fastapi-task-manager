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

    def create_project(self, data: ProjectCreate, owner_id: int):
        try:
            project = self.project_repo.create(
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

    def get_project(self, project_id: int):
        project = self.project_repo.get(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    def update_project(self, project_id: int, data: ProjectUpdate, user_id: int):
        project = self.get_project(project_id)

        member = self.member_repo.get(project_id, user_id)
        if not member or member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to update this project",
            )
        
        update_data = data.model_dump(exclude_unset=True)
        before = {
            "title": project.title,
            "description": project.description,
            "status": project.status,
        }

        try:
            project = self.project_repo.update(project, update_data)

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
        project = self.get_project(project_id)
        member = self.member_repo.get(project_id, user_id)
        if not member or member.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owner can delete project",
            )
        self.project_repo.delete(project)
