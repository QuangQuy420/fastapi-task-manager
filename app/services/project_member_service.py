from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectMemberCreate


class ProjectMemberService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)

    def add_member(self, data: ProjectMemberCreate, acting_user_id: int):
        project = self.project_repo.get(data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        acting_member = self.member_repo.get(data.project_id, acting_user_id)
        if not acting_member or acting_member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to add members",
            )

        existing = self.member_repo.get(data.project_id, data.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already member of project",
            )

        return self.member_repo.add_member(
            project_id=data.project_id,
            user_id=data.user_id,
            role=data.role,
        )

    def remove_member(self, project_id: int, user_id: int, acting_user_id: int):
        acting_member = self.member_repo.get(project_id, acting_user_id)
        if not acting_member or acting_member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to remove members",
            )

        member = self.member_repo.get(project_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        self.member_repo.remove_member(member)
