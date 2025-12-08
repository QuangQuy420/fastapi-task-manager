from typing import Iterable

from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember


class ProjectMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, project_id: int, user_id: int) -> ProjectMember | None:
        return (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )

    def list_by_project(self, project_id: int) -> Iterable[ProjectMember]:
        return (
            self.db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id)
            .all()
        )

    def add_member(self, project_id: int, user_id: int, role: str) -> ProjectMember:
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        self.db.add(member)
        # no commit here - service layer should handle transactions
        return member

    def remove_member(self, member: ProjectMember) -> None:
        self.db.delete(member)
        self.db.commit()
