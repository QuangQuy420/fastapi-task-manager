from typing import Iterable

from sqlalchemy.orm import Session

from app.core.enums import ProjectStatus
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_user_projects(self, user_id: int) -> Iterable[Project]:
        return (
            self.db.query(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .filter(
                ProjectMember.user_id == user_id,
                Project.deleted_at.is_(None)
            )
            .all()
        )

    def delete_project(self, project: Project) -> None:
        # Use base soft_delete method
        self.soft_delete(project)
        project.status = ProjectStatus.ARCHIVED.value
   