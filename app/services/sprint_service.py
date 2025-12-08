from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.project_repository import ProjectRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.sprint_repository import SprintRepository
from app.schemas.project import SprintCreate, SprintUpdate


class SprintService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)
        self.sprint_repo = SprintRepository(db)

    def create_sprint(self, data: SprintCreate, user_id: int):
        # check project exists & user is member
        project = self.project_repo.get(data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        member = self.member_repo.get(data.project_id, user_id)
        if not member or member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to create sprints in this project",
            )

        sprint_data = data.model_dump()
        return self.sprint_repo.create(sprint_data)

    def update_sprint(self, sprint_id: int, data: SprintUpdate, user_id: int):
        sprint = self.sprint_repo.get(sprint_id)
        if not sprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sprint not found",
            )

        member = self.member_repo.get(sprint.project_id, user_id)
        if not member or member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to update this sprint",
            )

        update_data = data.model_dump(exclude_unset=True)
        return self.sprint_repo.update(sprint, update_data)

    def delete_sprint(self, sprint_id: int, user_id: int):
        sprint = self.sprint_repo.get(sprint_id)
        if not sprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sprint not found",
            )

        member = self.member_repo.get(sprint.project_id, user_id)
        if not member or member.role not in ("owner", "maintainer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to delete this sprint",
            )

        self.sprint_repo.delete(sprint)
