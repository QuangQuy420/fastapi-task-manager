from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    """
    Repository handles direct DB operations (CRUD) for Task.
    Keeps raw SQLAlchemy operations out of the service layer.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------------------
    # Query Methods
    # ---------------------

    def list(self) -> list[Task]:
        """
        Return all tasks.
        extend with filters (status, priority, assigned_to...) later
        """
        return self.db.query(Task).order_by(Task.created_at.desc()).all()

    def get(self, task_id: int) -> Task | None:
        """
        Return a task by ID, or None.
        """
        return (
            self.db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

    # ---------------------
    # Create / Update / Delete
    # ---------------------

    def create(self, task_in: TaskCreate) -> Task:
        """
        Create a new Task from TaskCreate schema.
        """
        task = Task(**task_in.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, task_in: TaskUpdate) -> Task:
        """
        Update a Task instance using TaskUpdate schema.
        Only fields that were sent (exclude_unset=True) will be updated.
        """
        data = task_in.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        """
        Delete a Task.
        """
        self.db.delete(task)
        self.db.commit()
