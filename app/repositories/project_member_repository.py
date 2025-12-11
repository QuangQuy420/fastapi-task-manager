from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_member import ProjectMember
from app.repositories.base_repository import BaseRepository


class ProjectMemberRepository(BaseRepository[ProjectMember]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectMember, db)

    async def get_member_project(
        self, project_id: int, user_id: int
    ) -> ProjectMember | None:
        query = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def check_permissions(
        self, project_id: int, user_id: int, required_roles: list[str]
    ):
        member = await self.get_member_project(project_id, user_id)
        if not member or member.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to perform action",
            )

    async def list_by_project(self, project_id: int) -> List[ProjectMember]:
        query = select(ProjectMember).where(ProjectMember.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    def add_member(self, project_id: int, user_id: int, role: str) -> ProjectMember:
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        self.db.add(member)
        return member
