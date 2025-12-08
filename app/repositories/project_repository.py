from typing import Iterable, Optional

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.enums import ProjectStatus
from app.models.project import Project
from app.models.project_member import ProjectMember


class ProjectRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_project_by_id(self, project_id: int, for_update=False) -> Optional[Project]:
        query = self.db.query(Project).filter(Project.id == project_id)

        if for_update:
            query = query.with_for_update()

        return query.one_or_none()

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

    def create_project(self, *, title: str, description: str | None, managed_by: int) -> Project:
        project = Project(
            title=title,
            description=description,
            managed_by=managed_by,
        )
        self.db.add(project)
        # Note: No commit here. The Service layer handles the "Unit of Work" (Commit).
        return project

    def update_project(self, project: Project, data: dict) -> Project:
        for field, value in data.items():
            setattr(project, field, value)

        self.db.flush()
        return project

    def delete_project(self, project: Project) -> None:
        project.deleted_at = func.now()
        project.status = ProjectStatus.ARCHIVED.value

        self.db.flush()
        return None
