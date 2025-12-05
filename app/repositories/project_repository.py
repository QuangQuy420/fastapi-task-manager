from typing import Iterable

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, project_id: int) -> Project | None:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def list_for_user(self, user_id: int) -> Iterable[Project]:
        return (
            self.db.query(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .filter(ProjectMember.user_id == user_id)
            .all()
        )

    def create(self, *, title: str, description: str | None, managed_by: int) -> Project:
        project = Project(
            title=title,
            description=description,
            managed_by=managed_by,
        )
        self.db.add(project)
        # no commit here - service layer should handle transactions
        return project

    def update(self, project: Project, data: dict) -> Project:
        for field, value in data.items():
            setattr(project, field, value)

        self.db.flush()
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()
