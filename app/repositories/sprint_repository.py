from typing import Iterable

from sqlalchemy.orm import Session

from app.models.sprint import Sprint


class SprintRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, sprint_id: int) -> Sprint | None:
        return self.db.query(Sprint).filter(Sprint.id == sprint_id).first()

    def list_by_project(self, project_id: int) -> Iterable[Sprint]:
        return (
            self.db.query(Sprint)
            .filter(Sprint.project_id == project_id)
            .order_by(Sprint.start_date)
            .all()
        )

    def create(self, data: dict) -> Sprint:
        sprint = Sprint(**data)
        self.db.add(sprint)
        self.db.commit()
        self.db.refresh(sprint)
        return sprint

    def update(self, sprint: Sprint, data: dict) -> Sprint:
        for field, value in data.items():
            setattr(sprint, field, value)
        self.db.commit()
        self.db.refresh(sprint)
        return sprint

    def delete(self, sprint: Sprint) -> None:
        self.db.delete(sprint)
        self.db.commit()
