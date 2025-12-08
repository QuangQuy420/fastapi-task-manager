from sqlalchemy.orm import Session
from app.models.project_history import ProjectHistory


class ProjectHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_history(
        self,
        meta: dict,
        details: dict | None = None,
    ) -> ProjectHistory:
        """
        Create a new project history record.
        :param meta: {
            "project_id": int,
            "changed_by": int,
            "action": str,
            "title": str (optional),
            "description": str (optional),
            "status": str (optional),
        }
        :param details: Optional additional details about the change.
        """
        history = ProjectHistory(
            **meta,
            details=details,
        )

        self.db.add(history)

        return history