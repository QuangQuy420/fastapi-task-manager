from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectMemberCreate
from app.services.base_service import BaseService


class ProjectMemberService(BaseService[ProjectMemberRepository]):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        member_repo = ProjectMemberRepository(db)
        super().__init__(db, member_repo)
        self.member_repo = member_repo

    async def add_member(self, data: ProjectMemberCreate, acting_user_id: int):
        project = await self.project_repo.get_by_id(data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        acting_member = await self.member_repo.get_member_project(
            data.project_id, acting_user_id
        )
        if not acting_member or acting_member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to add members",
            )

        existing = await self.member_repo.get_member_project(
            data.project_id, data.user_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already member of project",
            )

        self.member_repo.add_member(
            project_id=data.project_id,
            user_id=data.user_id,
            role=data.role,
        )

        await self.commit_or_rollback()
        return True

    async def remove_member(self, project_id: int, user_id: int, acting_user_id: int):
        acting_member = await self.member_repo.get_member_project(
            project_id, acting_user_id
        )
        if not acting_member or acting_member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to remove members",
            )

        member = await self.member_repo.get_member_project(project_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        await self.db.delete(member)
        await self.commit_or_rollback()
