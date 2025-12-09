from typing import Iterable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.project_member import ProjectMember
from app.repositories.base_repository import BaseRepository


class ProjectMemberRepository(BaseRepository[ProjectMember]):
    def __init__(self, db: Session):
        super().__init__(ProjectMember, db)

    def get_member_project(self, project_id: int, user_id: int) -> ProjectMember | None:
        return (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )
    
    def check_permissions(self, project_id: int, user_id: int, required_roles: list[str]):
        member = self.get_member_project(project_id, user_id)
        if not member or member.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to perform action",
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

    # def remove_member(self, member: ProjectMember) -> None:
    #     self.db.delete(member)
    #     self.db.commit()
